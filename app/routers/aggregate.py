from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository
from app.deps import get_db_session

router = APIRouter(prefix="/aggregate", tags=["aggregate"])

@router.get("/user-to-host", response_class=ORJSONResponse)
async def aggregate_user_to_host(
    start_ts: datetime | None = Query(default=None),
    end_ts: datetime | None = Query(default=None),
    user: str | None = Query(default=None),
    n: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
):
    rows = await repository.user_to_host(db, start_ts, end_ts, user, n)
    return rows
