import requests
from fastapi import HTTPException, status

from app.core.config import settings


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate embedding for empty text."
        )

    payload = {
        "model": settings.OLLAMA_EMBED_MODEL,
        "input": text
    }

    try:
        response = requests.post(
            settings.OLLAMA_EMBED_URL,
            json=payload,
            timeout=120
        )
    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding service unavailable: {str(error)}"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"Embedding service error: {response.status_code} - "
                f"{response.text}"
            )
        )

    data = response.json()

    embeddings = data.get("embeddings")

    if isinstance(embeddings, list) and len(embeddings) > 0:
        first_embedding = embeddings[0]

        if isinstance(first_embedding, list):
            return first_embedding

    legacy_embedding = data.get("embedding")

    if isinstance(legacy_embedding, list):
        return legacy_embedding

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Embedding service returned an invalid response."
    )


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    clean_texts = [
        text.strip()
        for text in texts
        if text.strip()
    ]

    if not clean_texts:
        return []

    payload = {
        "model": settings.OLLAMA_EMBED_MODEL,
        "input": clean_texts
    }

    try:
        response = requests.post(
            settings.OLLAMA_EMBED_URL,
            json=payload,
            timeout=300
        )
    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Embedding service unavailable: {str(error)}"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"Embedding service error: {response.status_code} - "
                f"{response.text}"
            )
        )

    data = response.json()
    embeddings = data.get("embeddings")

    if not isinstance(embeddings, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding service returned invalid embeddings."
        )

    if len(embeddings) != len(clean_texts):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding count does not match input count."
        )

    return embeddings