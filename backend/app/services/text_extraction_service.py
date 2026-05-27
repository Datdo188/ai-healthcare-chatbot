import os

from fastapi import HTTPException, status
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            text = file.read()
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read TXT document."
        )

    text = text.strip()

    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TXT document is empty."
        )

    return text


def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
    except (PdfReadError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read this PDF document."
        )

    text_parts = []

    try:
        for page in reader.pages:
            text = page.extract_text()

            if text:
                text_parts.append(text.strip())
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from this PDF document."
        )

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No extractable text found in this PDF. "
                "Scanned image PDFs are not supported yet."
            )
        )

    return full_text


def extract_text_from_document(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found."
        )

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document path."
        )

    _, extension = os.path.splitext(file_path.lower())

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported document type."
    )