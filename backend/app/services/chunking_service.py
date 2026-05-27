from fastapi import HTTPException, status

from app.core.config import settings


def split_text_into_chunks(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None
) -> list[str]:
    if not text.strip():
        return []

    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap if overlap is not None else settings.CHUNK_OVERLAP

    if chunk_size <= 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid chunk size configuration."
        )

    if overlap < 0 or overlap >= chunk_size:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid chunk overlap configuration."
        )

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks