from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.models.schemas import (
    ChatHistoryItem,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ChatSource,
    MessageResponse,
)
from app.services.auth_service import get_current_user
from app.services.chat_service import (
    delete_all_chat_history,
    delete_single_chat_message,
    get_chat_history_items,
    handle_chat_message,
)

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
    result = handle_chat_message(
        db=db,
        user=current_user,
        question=request.question
    )

    return ChatResponse(
        question=result["question"],
        answer=result["answer"],
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
            for source in result["sources"]
        ]
    )


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history_items = get_chat_history_items(
        db=db,
        user=current_user,
        limit=limit
    )

    return ChatHistoryResponse(
        history=[
            ChatHistoryItem(
                id=item["id"],
                question=item["question"],
                answer=item["answer"],
                sources=[
                    ChatSource(
                        filename=source["filename"],
                        chunk_index=source["chunk_index"],
                        score=source["score"]
                    )
                    for source in item["sources"]
                ],
                created_at=item["created_at"]
            )
            for item in history_items
        ],
        count=len(history_items)
    )


@router.delete("/history", response_model=MessageResponse)
def delete_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted_count = delete_all_chat_history(
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
    delete_single_chat_message(
        db=db,
        user=current_user,
        message_id=message_id
    )

    return MessageResponse(
        message="Chat message deleted successfully."
    )