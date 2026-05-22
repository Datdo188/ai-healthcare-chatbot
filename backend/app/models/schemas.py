from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User's healthcare-related question"
    )


class ChatResponse(BaseModel):
    question: str
    answer: str