import requests
from fastapi import APIRouter
from app.core.config import settings

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