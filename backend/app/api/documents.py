from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentItem,
    DocumentPreviewResponse,
    DocumentChunkResponse,
    DocumentIndexResponse,
    DocumentDeleteResponse,
    DocumentSearchResponse,
    RetrievedChunk,
)
from app.services.auth_service import get_current_user
from app.services.document_metadata_service import (
    create_document_metadata,
    delete_document_metadata,
    get_user_document_by_saved_filename,
    list_user_documents,
    update_document_status,
)
from app.services.document_service import (
    delete_document_file,
    save_uploaded_document,
)
from app.services.text_extraction_service import extract_text_from_document
from app.services.chunking_service import split_text_into_chunks
from app.services.rag_index_service import (
    delete_document_chunks,
    index_document_chunks,
    search_chunks_by_keyword,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved_file = save_uploaded_document(file)

    document = create_document_metadata(
        db=db,
        user=current_user,
        original_filename=saved_file["original_filename"],
        saved_filename=saved_file["saved_filename"],
        path=saved_file["path"],
        status_value="uploaded"
    )

    return DocumentUploadResponse(
        message="Document uploaded successfully",
        id=document.id,
        original_filename=document.original_filename,
        saved_filename=document.saved_filename,
        path=document.path,
        status=document.status
    )


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documents = list_user_documents(
        db=db,
        user=current_user
    )

    return DocumentListResponse(
        documents=[
            DocumentItem(
                id=document.id,
                original_filename=document.original_filename,
                saved_filename=document.saved_filename,
                path=document.path,
                status=document.status,
                created_at=document.created_at
            )
            for document in documents
        ],
        count=len(documents)
    )


@router.get("/search/", response_model=DocumentSearchResponse)
def search_documents(
    query: str,
    top_k: int = 3,
    current_user: User = Depends(get_current_user)
):
    results = search_chunks_by_keyword(
        query=query,
        user_id=current_user.id,
        top_k=top_k
    )

    return DocumentSearchResponse(
        query=query,
        results=[
            RetrievedChunk(
                filename=result["filename"],
                chunk_index=result["chunk_index"],
                content=result["content"],
                score=result["score"],
            )
            for result in results
        ],
        count=len(results),
    )


@router.get("/{filename}/preview", response_model=DocumentPreviewResponse)
def preview_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = get_user_document_by_saved_filename(
        db=db,
        user=current_user,
        saved_filename=filename
    )

    text = extract_text_from_document(document.path)
    preview = text[:1000]

    return DocumentPreviewResponse(
        filename=document.saved_filename,
        path=document.path,
        preview=preview,
        character_count=len(text),
    )


@router.get("/{filename}/chunks", response_model=DocumentChunkResponse)
def chunk_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = get_user_document_by_saved_filename(
        db=db,
        user=current_user,
        saved_filename=filename
    )

    text = extract_text_from_document(document.path)
    chunks = split_text_into_chunks(text)

    return DocumentChunkResponse(
        filename=document.saved_filename,
        chunk_count=len(chunks),
        chunks=chunks[:5],
    )


@router.post("/{filename}/index", response_model=DocumentIndexResponse)
def index_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = get_user_document_by_saved_filename(
        db=db,
        user=current_user,
        saved_filename=filename
    )

    text = extract_text_from_document(document.path)
    chunks = split_text_into_chunks(text)

    result = index_document_chunks(
        filename=document.saved_filename,
        chunks=chunks,
        user_id=current_user.id
    )

    update_document_status(
        db=db,
        document=document,
        status_value="indexed"
    )

    return DocumentIndexResponse(
        filename=result["filename"],
        indexed_chunks=result["indexed_chunks"],
        message=result["message"],
    )


@router.delete("/{filename}", response_model=DocumentDeleteResponse)
def delete_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = get_user_document_by_saved_filename(
        db=db,
        user=current_user,
        saved_filename=filename
    )

    deleted_file = delete_document_file(document.path)

    deleted_chunks = delete_document_chunks(
        filename=document.saved_filename,
        user_id=current_user.id
    )

    delete_document_metadata(
        db=db,
        document=document
    )

    return DocumentDeleteResponse(
        filename=filename,
        deleted_file=deleted_file,
        deleted_index_chunks=deleted_chunks,
        message="Document deleted successfully."
    )