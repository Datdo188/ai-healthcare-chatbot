from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models import User
from app.models.schemas import (
    DocumentChunkResponse,
    DocumentDeleteResponse,
    DocumentIndexResponse,
    DocumentItem,
    DocumentListResponse,
    DocumentPreviewResponse,
    DocumentSearchResponse,
    DocumentUploadResponse,
    RetrievedChunk,
)
from app.services.auth_service import get_current_user
from app.services.document_processing_service import (
    delete_user_document,
    get_document_chunks,
    get_document_preview,
    index_user_document,
    list_documents_for_user,
    search_user_documents,
    upload_user_document,
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
    document = upload_user_document(
        db=db,
        user=current_user,
        file=file
    )

    return DocumentUploadResponse(
        message="Document uploaded successfully",
        id=document.id,
        original_filename=document.original_filename,
        saved_filename=document.saved_filename,
        status=document.status
    )


@router.get("/", response_model=DocumentListResponse)
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documents = list_documents_for_user(
        db=db,
        user=current_user
    )

    return DocumentListResponse(
        documents=[
            DocumentItem(
                id=document.id,
                original_filename=document.original_filename,
                saved_filename=document.saved_filename,
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
    top_k: int = settings.RAG_TOP_K,
    current_user: User = Depends(get_current_user)
):
    results = search_user_documents(
        user=current_user,
        query=query,
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
    result = get_document_preview(
        db=db,
        user=current_user,
        filename=filename
    )

    return DocumentPreviewResponse(
        filename=result["filename"],
        preview=result["preview"],
        character_count=result["character_count"]
    )


@router.get("/{filename}/chunks", response_model=DocumentChunkResponse)
def chunk_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = get_document_chunks(
        db=db,
        user=current_user,
        filename=filename
    )

    return DocumentChunkResponse(
        filename=result["filename"],
        chunk_count=result["chunk_count"],
        chunks=result["chunks"]
    )


@router.post("/{filename}/index", response_model=DocumentIndexResponse)
def index_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = index_user_document(
        db=db,
        user=current_user,
        filename=filename
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
    result = delete_user_document(
        db=db,
        user=current_user,
        filename=filename
    )

    return DocumentDeleteResponse(
        filename=result["filename"],
        deleted_file=result["deleted_file"],
        deleted_index_chunks=result["deleted_index_chunks"],
        message=result["message"]
    )