import os
from typing import List

import chromadb
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.embedding_service import generate_embedding, generate_embeddings

os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)

_chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH
)

_collection = _chroma_client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    metadata={
        "description": "Medical document chunks for AI Healthcare Chatbot",
        "hnsw:space": "cosine"
    }
)


def build_chunk_id(
    user_id: int,
    filename: str,
    chunk_index: int
) -> str:
    return f"user_{user_id}__file_{filename}__chunk_{chunk_index}"


def index_document_chunks(
    filename: str,
    chunks: List[str],
    user_id: int
) -> dict:
    """
    Store document chunks in ChromaDB using real vector embeddings.
    """

    clean_chunks = [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]

    if not clean_chunks:
        return {
            "filename": filename,
            "indexed_chunks": 0,
            "message": "No valid chunks to index."
        }

    delete_document_chunks(
        filename=filename,
        user_id=user_id
    )

    ids = []
    metadatas = []

    for chunk_index, _chunk in enumerate(clean_chunks):
        ids.append(
            build_chunk_id(
                user_id=user_id,
                filename=filename,
                chunk_index=chunk_index
            )
        )

        metadatas.append({
            "user_id": user_id,
            "filename": filename,
            "chunk_index": chunk_index
        })

    embeddings = generate_embeddings(clean_chunks)

    if len(embeddings) != len(clean_chunks):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding count does not match chunk count."
        )

    _collection.upsert(
        ids=ids,
        documents=clean_chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "filename": filename,
        "indexed_chunks": len(clean_chunks),
        "message": "Document chunks indexed successfully with vector embeddings."
    }


def delete_document_chunks(
    filename: str,
    user_id: int
) -> int:
    """
    Delete all vector chunks for a user's document from ChromaDB.
    """

    existing = _collection.get(
        where={
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"filename": {"$eq": filename}}
            ]
        },
        include=["metadatas"]
    )

    ids = existing.get("ids", [])

    if not ids:
        return 0

    _collection.delete(ids=ids)

    return len(ids)


def search_relevant_chunks(
    query: str,
    user_id: int,
    top_k: int = 3
) -> list[dict]:
    """
    Search document chunks using vector similarity.
    Lower Chroma distance means more similar.
    This returns score as similarity-like value: 1 - distance.
    """

    if not query.strip():
        return []

    query_embedding = generate_embedding(query)

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "user_id": {
                "$eq": user_id
            }
        },
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matched_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        similarity_score = 1.0 - float(distance)

        matched_chunks.append({
            "filename": metadata["filename"],
            "chunk_index": metadata["chunk_index"],
            "content": document,
            "score": similarity_score
        })

    return matched_chunks


def search_chunks_by_keyword(
    query: str,
    user_id: int,
    top_k: int = 3
) -> list[dict]:
    """
    Backward-compatible function name.
    Internally this now performs real vector search, not keyword search.
    """

    return search_relevant_chunks(
        query=query,
        user_id=user_id,
        top_k=top_k
    )