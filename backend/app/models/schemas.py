from datetime import datetime

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User's healthcare-related question"
    )


class ChatSource(BaseModel):
    filename: str
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    disclaimer: str
    sources: list[ChatSource] = []


class ChatHistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    sources: list[ChatSource] = []
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    history: list[ChatHistoryItem]
    count: int


class DocumentUploadResponse(BaseModel):
    message: str
    id: int
    original_filename: str
    saved_filename: str
    path: str
    status: str


class DocumentItem(BaseModel):
    id: int
    original_filename: str
    saved_filename: str
    path: str
    status: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentItem]
    count: int


class DocumentPreviewResponse(BaseModel):
    filename: str
    path: str
    preview: str
    character_count: int


class DocumentChunkResponse(BaseModel):
    filename: str
    chunk_count: int
    chunks: list[str]


class DocumentIndexResponse(BaseModel):
    filename: str
    indexed_chunks: int
    message: str


class DocumentDeleteResponse(BaseModel):
    filename: str
    deleted_file: bool
    deleted_index_chunks: int
    message: str


class RetrievedChunk(BaseModel):
    filename: str
    chunk_index: int
    content: str
    score: float


class DocumentSearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
    count: int


class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse