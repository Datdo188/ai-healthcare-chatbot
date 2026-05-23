from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.models.schemas import (
    ChatHistoryItem,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatSource,
    MessageResponse,
)
from app.services.auth_service import get_current_user
from app.services.chat_history_service import (
    delete_user_chat_history,
    delete_user_chat_message,
    get_user_chat_history,
    parse_sources_json,
    save_chat_message,
)
from app.services.llm_service import generate_response
from app.services.rag_index_service import search_chunks_by_keyword

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    retrieved_chunks = search_chunks_by_keyword(
        query=request.question,
        user_id=current_user.id,
        top_k=3
    )

    context = "\n\n".join(
        [
            f"Source: {chunk['filename']} | Chunk {chunk['chunk_index']}\n{chunk['content']}"
            for chunk in retrieved_chunks
        ]
    )

    answer = generate_response(
        question=request.question,
        context=context
    )

    source_items = [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "score": chunk["score"]
        }
        for chunk in retrieved_chunks
    ]

    save_chat_message(
        db=db,
        user=current_user,
        question=request.question,
        answer=answer,
        sources=source_items
    )

    return ChatResponse(
        question=request.question,
        answer=answer,
        disclaimer=(
            "This chatbot provides general health information only "
            "and does not replace professional medical advice."
        ),
        sources=[
            ChatSource(
                filename=source["filename"],
                chunk_index=source["chunk_index"],
                score=source["score"]
            )
            for source in source_items
        ]
    )


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat_messages = get_user_chat_history(
        db=db,
        user=current_user,
        limit=limit
    )

    history_items = []

    for message in chat_messages:
        sources = parse_sources_json(message.sources_json)

        history_items.append(
            ChatHistoryItem(
                id=message.id,
                question=message.question,
                answer=message.answer,
                sources=[
                    ChatSource(
                        filename=source["filename"],
                        chunk_index=source["chunk_index"],
                        score=source["score"]
                    )
                    for source in sources
                ],
                created_at=message.created_at
            )
        )

    return ChatHistoryResponse(
        history=history_items,
        count=len(history_items)
    )


@router.delete("/history", response_model=MessageResponse)
def delete_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted_count = delete_user_chat_history(
        db=db,
        user=current_user
    )

    return MessageResponse(
        message=f"Deleted {deleted_count} chat messages."
    )


@router.delete("/history/{message_id}", response_model=MessageResponse)
def delete_chat_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delete_user_chat_message(
        db=db,
        user=current_user,
        message_id=message_id
    )

    return MessageResponse(
        message="Chat message deleted successfully."
    )