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


settings = Settings()