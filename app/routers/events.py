from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository
from app.deps import get_db_session
from app.schemas import ResultFilter

router = APIRouter(prefix="/events", tags=["events"])

@router.get("", response_class=ORJSONResponse)
async def get_events(
    start_ts: datetime | None = Query(default=None),
    end_ts: datetime | None = Query(default=None),
    user: str | None = Query(default=None),
    src_host: str | None = Query(default=None),
    dst_host: str | None = Query(default=None),
    result: ResultFilter | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    cursor_ts: datetime | None = Query(default=None),
    cursor_id: int | None = Query(default=None, ge=1),
    db: AsyncSession = Depends(get_db_session),
):
    if (cursor_ts is None) != (cursor_id is None):
        return ORJSONResponse(
            status_code=422,
            content={"detail": "cursor_ts and cursor_id must be provided together"},
        )

    rows = await repository.search_events(
        db=db,
        start_ts=start_ts,
        end_ts=end_ts,
        user=user,
        src_host=src_host,
        dst_host=dst_host,
        result=result,
        limit=limit,
        offset=offset,
        cursor_ts=cursor_ts,
        cursor_id=cursor_id,
    )
    return rows
