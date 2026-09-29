import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.collections.router import router as collections_router
from app.core.config import get_settings
from app.health.router import router as health_router

# Root stays at WARNING so third-party libraries (httpx, qdrant_client, groq)
# don't spam per-request logs; only this app's own loggers (app.*, e.g.
# app.rag.reranker) are raised to INFO to surface things like reranker scores.
logging.basicConfig(level=logging.WARNING)
logging.getLogger("app").setLevel(logging.INFO)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="MediAssist Health Network internal assistant - RBAC-scoped hybrid + SQL RAG.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(collections_router)
