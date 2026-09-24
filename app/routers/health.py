from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository
from app.db import ping_db
from app.deps import get_db_session
from app.schemas import HealthResponse, StatsResponse
from app.settings import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    db_status = "ok"
    try:
        await ping_db()
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok", db=db_status, version=settings.app_version)


@router.get("/stats", response_model=StatsResponse)
async def stats(db: AsyncSession = Depends(get_db_session)) -> StatsResponse:
    data = await repository.get_stats(db)
    return StatsResponse(**data)
