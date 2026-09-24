from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    db: str
    version: str


class StatsResponse(BaseModel):
    count: int
    min_ts: datetime | None
    max_ts: datetime | None


class EventOut(BaseModel):
    id: int
    ts: datetime
    user_name: str | None
    src_host: str | None
    dst_host: str | None
    auth_type: str | None
    result: str | None


class TopUserOut(BaseModel):
    user: str
    fail_count: int


class TopHostOut(BaseModel):
    host: str
    count: int


class TimelineOut(BaseModel):
    bucket_start: datetime
    count: int


class UserHostAggOut(BaseModel):
    user: str
    host: str
    count: int


ResultFilter = Literal["SUCCESS", "FAIL"]
BucketFilter = Literal["minute", "hour", "day"]


class EventsQuery(BaseModel):
    start_ts: datetime | None = None
    end_ts: datetime | None = None
    user: str | None = None
    src_host: str | None = None
    dst_host: str | None = None
    result: ResultFilter | None = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
