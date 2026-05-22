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
    disclaimer: str


class DocumentUploadResponse(BaseModel):
    message: str
    original_filename: str
    saved_filename: str
    path: str

class DocumentItem(BaseModel):
    filename: str
    path: str


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