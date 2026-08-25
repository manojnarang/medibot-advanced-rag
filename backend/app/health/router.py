from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.db.sqlite import is_database_reachable

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_connected: bool


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database_connected=is_database_reachable(),
    )
