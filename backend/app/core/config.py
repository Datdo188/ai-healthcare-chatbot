import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Healthcare Chatbot")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    OLLAMA_URL: str = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    OLLAMA_EMBED_URL: str = os.getenv(
        "OLLAMA_EMBED_URL",
        "http://localhost:11434/api/embed"
    )
    OLLAMA_EMBED_MODEL: str = os.getenv(
        "OLLAMA_EMBED_MODEL",
        "nomic-embed-text"
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_healthcare"
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "change-this-secret-key-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/medical_docs")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
    MIN_RELEVANCE_SCORE: float = float(
        os.getenv("MIN_RELEVANCE_SCORE", "0.25")
    )
    MAX_CONTEXT_CHARS: int = int(
        os.getenv("MAX_CONTEXT_CHARS", "6000")
    )

    CHROMA_DB_PATH: str = os.getenv(
        "CHROMA_DB_PATH",
        "data/chroma_db"
    )
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "medical_documents"
    )


settings = Settings()