from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.core.config import settings
from app.db.database import init_db_with_retry


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_with_retry()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AI Healthcare Chatbot",
    version=settings.APP_VERSION,
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} Backend is running"
    }


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(documents_router)