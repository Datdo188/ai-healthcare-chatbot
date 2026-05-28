from sqlalchemy.orm import Session

from app.models import User
from app.services.chat_history_service import (
    delete_user_chat_history,
    delete_user_chat_message,
    get_user_chat_history,
    parse_sources_json,
    save_chat_message,
)
from app.services.llm_service import generate_response
from app.services.rag_service import build_rag_context


def handle_chat_message(
    db: Session,
    user: User,
    question: str
) -> dict:
    """
    Handle a full chat request:
    - retrieve relevant RAG context
    - call LLM
    - save chat history
    - return answer and sources
    """

    rag_result = build_rag_context(
        query=question,
        user_id=user.id
    )

    answer = generate_response(
        question=question,
        context=rag_result["context"]
    )

    save_chat_message(
        db=db,
        user=user,
        question=question,
        answer=answer,
        sources=rag_result["sources"]
    )

    return {
        "question": question,
        "answer": answer,
        "sources": rag_result["sources"]
    }


def get_chat_history_items(
    db: Session,
    user: User,
    limit: int = 20
) -> list[dict]:
    """
    Return user chat history in API-ready dict format.
    """

    chat_messages = get_user_chat_history(
        db=db,
        user=user,
        limit=limit
    )

    history_items = []

    for message in chat_messages:
        sources = parse_sources_json(message.sources_json)

        history_items.append({
            "id": message.id,
            "question": message.question,
            "answer": message.answer,
            "sources": sources,
            "created_at": message.created_at
        })

    return history_items


def delete_all_chat_history(
    db: Session,
    user: User
) -> int:
    """
    Delete all chat history for a user.
    """

    return delete_user_chat_history(
        db=db,
        user=user
    )


def delete_single_chat_message(
    db: Session,
    user: User,
    message_id: int
) -> None:
    """
    Delete one chat message owned by the user.
    """

    delete_user_chat_message(
        db=db,
        user=user,
        message_id=message_id
    )