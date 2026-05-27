from app.core.config import settings
from app.services.rag_index_service import search_relevant_chunks


def retrieve_relevant_chunks(
    query: str,
    user_id: int,
    top_k: int | None = None
) -> list[dict]:
    """
    Retrieve relevant document chunks for a user's question.
    """

    return search_relevant_chunks(
        query=query,
        user_id=user_id,
        top_k=top_k or settings.RAG_TOP_K
    )


def build_context_from_chunks(chunks: list[dict]) -> str:
    """
    Build LLM context from retrieved chunks and limit its size.
    """

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"Source: {chunk['filename']} | "
            f"Chunk {chunk['chunk_index']}\n"
            f"{chunk['content']}"
        )

    context = "\n\n".join(context_parts)

    if len(context) > settings.MAX_CONTEXT_CHARS:
        context = context[:settings.MAX_CONTEXT_CHARS]

    return context


def prepare_source_items(chunks: list[dict]) -> list[dict]:
    """
    Convert retrieved chunks into source metadata for API response/history.
    """

    return [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "score": chunk["score"]
        }
        for chunk in chunks
    ]


def build_rag_context(
    query: str,
    user_id: int,
    top_k: int | None = None
) -> dict:
    """
    Retrieve chunks, build context, and prepare sources.
    """

    chunks = retrieve_relevant_chunks(
        query=query,
        user_id=user_id,
        top_k=top_k
    )

    context = build_context_from_chunks(chunks)
    sources = prepare_source_items(chunks)

    return {
        "chunks": chunks,
        "context": context,
        "sources": sources
    }