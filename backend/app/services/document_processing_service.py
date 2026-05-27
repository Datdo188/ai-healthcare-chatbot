from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.models import UploadedDocument, User
from app.services.chunking_service import split_text_into_chunks
from app.services.document_metadata_service import (
    create_document_metadata,
    delete_document_metadata,
    get_user_document_by_saved_filename,
    list_user_documents,
    safe_update_document_status,
    update_document_status,
)
from app.services.document_service import (
    delete_document_file,
    save_uploaded_document,
)
from app.services.rag_index_service import (
    delete_document_chunks,
    index_document_chunks,
    search_relevant_chunks,
)
from app.services.text_extraction_service import extract_text_from_document


def upload_user_document(
    db: Session,
    user: User,
    file: UploadFile
) -> UploadedDocument:
    """
    Save uploaded file and create document metadata.
    If DB metadata creation fails, remove the saved physical file.
    """

    saved_file = save_uploaded_document(file)

    try:
        document = create_document_metadata(
            db=db,
            user=user,
            original_filename=saved_file["original_filename"],
            saved_filename=saved_file["saved_filename"],
            path=saved_file["path"],
            status_value="uploaded"
        )

        return document

    except Exception:
        delete_document_file(saved_file["path"])
        raise


def list_documents_for_user(
    db: Session,
    user: User
) -> list[UploadedDocument]:
    return list_user_documents(
        db=db,
        user=user
    )


def get_document_preview(
    db: Session,
    user: User,
    filename: str
) -> dict:
    document = get_user_document_by_saved_filename(
        db=db,
        user=user,
        saved_filename=filename
    )

    text = extract_text_from_document(document.path)

    return {
        "filename": document.saved_filename,
        "preview": text[:1000],
        "character_count": len(text)
    }


def get_document_chunks(
    db: Session,
    user: User,
    filename: str
) -> dict:
    document = get_user_document_by_saved_filename(
        db=db,
        user=user,
        saved_filename=filename
    )

    text = extract_text_from_document(document.path)
    chunks = split_text_into_chunks(text)

    return {
        "filename": document.saved_filename,
        "chunk_count": len(chunks),
        "chunks": chunks[:5]
    }


def index_user_document(
    db: Session,
    user: User,
    filename: str
) -> dict:
    """
    Index a user's document into ChromaDB.

    Status lifecycle:
    uploaded/indexed/failed -> indexing -> indexed
    uploaded/indexing/indexed -> failed if error happens
    """

    document = get_user_document_by_saved_filename(
        db=db,
        user=user,
        saved_filename=filename
    )

    update_document_status(
        db=db,
        document=document,
        status_value="indexing"
    )

    try:
        text = extract_text_from_document(document.path)
        chunks = split_text_into_chunks(text)

        if not chunks:
            safe_update_document_status(
                db=db,
                document=document,
                status_value="failed"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document did not produce any valid chunks."
            )

        result = index_document_chunks(
            filename=document.saved_filename,
            chunks=chunks,
            user_id=user.id
        )

        if result["indexed_chunks"] <= 0:
            safe_update_document_status(
                db=db,
                document=document,
                status_value="failed"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document did not produce valid chunks for indexing."
            )

        update_document_status(
            db=db,
            document=document,
            status_value="indexed"
        )

        return result

    except HTTPException:
        safe_update_document_status(
            db=db,
            document=document,
            status_value="failed"
        )
        raise

    except Exception as error:
        safe_update_document_status(
            db=db,
            document=document,
            status_value="failed"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document indexing failed: {str(error)}"
        )


def search_user_documents(
    user: User,
    query: str,
    top_k: int
) -> list[dict]:
    return search_relevant_chunks(
        query=query,
        user_id=user.id,
        top_k=top_k
    )


def delete_user_document(
    db: Session,
    user: User,
    filename: str
) -> dict:
    """
    Delete a user's document from:
    - ChromaDB vector index
    - local file storage
    - PostgreSQL metadata

    Missing physical file or missing vector chunks should not block metadata deletion.
    """

    document = get_user_document_by_saved_filename(
        db=db,
        user=user,
        saved_filename=filename
    )

    deleted_chunks = delete_document_chunks(
        filename=document.saved_filename,
        user_id=user.id
    )

    deleted_file = delete_document_file(document.path)

    delete_document_metadata(
        db=db,
        document=document
    )

    return {
        "filename": filename,
        "deleted_file": deleted_file,
        "deleted_index_chunks": deleted_chunks,
        "message": "Document deleted successfully."
    }