from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import generate_response

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = generate_response(request.question)

    return ChatResponse(
        question=request.question,
        answer=answer,
        disclaimer=(
            "This chatbot provides general health information only "
            "and does not replace professional medical advice."
        )
    )