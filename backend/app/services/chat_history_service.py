import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import ChatMessage, User


def save_chat_message(
    db: Session,
    user: User,
    question: str,
    answer: str,
    sources: list[dict]
) -> ChatMessage:
    chat_message = ChatMessage(
        user_id=user.id,
        question=question,
        answer=answer,
        sources_json=json.dumps(sources, ensure_ascii=False)
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    return chat_message


def get_user_chat_history(
    db: Session,
    user: User,
    limit: int = 20
) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )


def delete_user_chat_history(
    db: Session,
    user: User
) -> int:
    deleted_count = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .delete()
    )

    db.commit()

    return deleted_count


def delete_user_chat_message(
    db: Session,
    user: User,
    message_id: int
) -> None:
    message = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.id == message_id,
            ChatMessage.user_id == user.id
        )
        .first()
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found."
        )

    db.delete(message)
    db.commit()


def parse_sources_json(sources_json: str | None) -> list[dict]:
    if not sources_json:
        return []

    try:
        return json.loads(sources_json)
    except json.JSONDecodeError:
        return []