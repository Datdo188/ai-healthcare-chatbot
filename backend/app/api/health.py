import requests
from fastapi import APIRouter

from app.core.config import settings
from app.db.database import check_database_connection

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/ollama")
def ollama_health_check():
    try:
        base_url = settings.OLLAMA_URL.replace("/api/generate", "")
        response = requests.get(base_url, timeout=5)

        if response.status_code == 200:
            return {
                "status": "ok",
                "ollama_url": settings.OLLAMA_URL,
                "message": "Ollama service is reachable"
            }

        return {
            "status": "error",
            "ollama_url": settings.OLLAMA_URL,
            "message": f"Ollama returned status code {response.status_code}"
        }

    except requests.exceptions.RequestException as error:
        return {
            "status": "error",
            "ollama_url": settings.OLLAMA_URL,
            "message": str(error)
        }


@router.get("/database")
def database_health_check():
    is_connected = check_database_connection()

    if is_connected:
        return {
            "status": "ok",
            "database": "PostgreSQL",
            "message": "Database connection is healthy"
        }

    return {
        "status": "error",
        "database": "PostgreSQL",
        "message": "Database connection failed"
    }