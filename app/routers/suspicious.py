from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import repository
from app.deps import get_db_session
from app.schemas import BucketFilter, TimelineOut, TopHostOut, TopUserOut

router = APIRouter(prefix="/suspicious", tags=["suspicious"])


@router.get("/top-users", response_model=list[TopUserOut])
async def suspicious_top_users(
    start_ts: datetime | None = Query(default=None),
    end_ts: datetime | None = Query(default=None),
    n: int = Query(default=20, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
) -> list[TopUserOut]:
    rows = await repository.top_users_by_failures(db, start_ts, end_ts, n)
    return [TopUserOut(**row) for row in rows]


@router.get("/top-hosts", response_model=list[TopHostOut])
async def suspicious_top_hosts(
    start_ts: datetime | None = Query(default=None),
    end_ts: datetime | None = Query(default=None),
    n: int = Query(default=20, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
) -> list[TopHostOut]:
    rows = await repository.top_hosts(db, start_ts, end_ts, n)
    return [TopHostOut(**row) for row in rows]


@router.get("/user-timeline", response_model=list[TimelineOut])
async def suspicious_user_timeline(
    user: str = Query(..., min_length=1),
    start_ts: datetime | None = Query(default=None),
    end_ts: datetime | None = Query(default=None),
    bucket: BucketFilter = Query(default="hour"),
    db: AsyncSession = Depends(get_db_session),
) -> list[TimelineOut]:
    rows = await repository.user_timeline(db, user, start_ts, end_ts, bucket)
    return [TimelineOut(**row) for row in rows]
