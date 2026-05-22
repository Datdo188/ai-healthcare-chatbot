from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.documents import router as documents_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AI Healthcare Chatbot",
    version=settings.APP_VERSION
)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} Backend is running"
    }


app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)