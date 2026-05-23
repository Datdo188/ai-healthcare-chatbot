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

    CHROMA_DB_PATH: str = os.getenv(
        "CHROMA_DB_PATH",
        "data/chroma_db"
    )
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "medical_documents"
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


settings = Settings()