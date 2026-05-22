import os

from fastapi import APIRouter, UploadFile, File

from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentItem,
    DocumentPreviewResponse,
    DocumentChunkResponse
)
from app.services.document_service import (
    save_uploaded_document,
    list_uploaded_documents,
    UPLOAD_DIR
)
from app.services.text_extraction_service import extract_text_from_document
from app.services.chunking_service import split_text_into_chunks


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(file: UploadFile = File(...)):
    saved_file = save_uploaded_document(file)

    return DocumentUploadResponse(
        message="Document uploaded successfully",
        original_filename=saved_file["original_filename"],
        saved_filename=saved_file["saved_filename"],
        path=saved_file["path"]
    )


@router.get("/", response_model=DocumentListResponse)
def get_documents():
    documents = list_uploaded_documents()

    return DocumentListResponse(
        documents=[
            DocumentItem(
                filename=document["filename"],
                path=document["path"]
            )
            for document in documents
        ],
        count=len(documents)
    )


@router.get("/{filename}/preview", response_model=DocumentPreviewResponse)
def preview_document(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    text = extract_text_from_document(file_path)
    preview = text[:1000]

    return DocumentPreviewResponse(
        filename=filename,
        path=file_path,
        preview=preview,
        character_count=len(text)
    )


@router.get("/{filename}/chunks", response_model=DocumentChunkResponse)
def chunk_document(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    text = extract_text_from_document(file_path)
    chunks = split_text_into_chunks(text)

    return DocumentChunkResponse(
        filename=filename,
        chunk_count=len(chunks),
        chunks=chunks[:5]
    )