from datetime import datetime
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def get_stats(db: AsyncSession) -> dict:
    result = await db.execute(
        text("SELECT COUNT(*) AS count, MIN(ts) AS min_ts, MAX(ts) AS max_ts FROM auth_events")
    )
    row = result.mappings().one()
    return {"count": int(row["count"]), "min_ts": row["min_ts"], "max_ts": row["max_ts"]}


async def search_events(
    db: AsyncSession,
    start_ts: datetime | None,
    end_ts: datetime | None,
    user: str | None,
    src_host: str | None,
    dst_host: str | None,
    result: str | None,
    limit: int,
    offset: int,
    cursor_ts: datetime | None,
    cursor_id: int | None,
) -> list[dict]:
    base_sql = """
    SELECT id, ts, user_name, src_host, dst_host, auth_type, result
    FROM auth_events
    """
    clauses = []
    params: dict[str, object] = {"limit": limit, "offset": offset}

    if start_ts is not None:
        clauses.append("ts >= :start_ts")
        params["start_ts"] = start_ts
    if end_ts is not None:
        clauses.append("ts <= :end_ts")
        params["end_ts"] = end_ts
    if user is not None:
        clauses.append("user_name = :user")
        params["user"] = user
    if src_host is not None:
        clauses.append("src_host = :src_host")
        params["src_host"] = src_host
    if dst_host is not None:
        clauses.append("dst_host = :dst_host")
        params["dst_host"] = dst_host
    if result is not None:
        clauses.append("result = :result")
        params["result"] = result

    # Keyset pagination: stable and faster on deep pages.
    # If cursor is provided, we ignore offset and seek from last (ts, id).
    if cursor_ts is not None and cursor_id is not None:
        clauses.append("(ts, id) < (:cursor_ts, :cursor_id)")
        params["cursor_ts"] = cursor_ts
        params["cursor_id"] = cursor_id

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    if cursor_ts is not None and cursor_id is not None:
        sql = f"{base_sql}{where_sql} ORDER BY ts DESC, id DESC LIMIT :limit"
    else:
        sql = f"{base_sql}{where_sql} ORDER BY ts DESC, id DESC LIMIT :limit OFFSET :offset"
    res = await db.execute(text(sql), params)
    return [dict(row) for row in res.mappings().all()]


async def top_users_by_failures(
    db: AsyncSession, start_ts: datetime | None, end_ts: datetime | None, n: int
) -> list[dict]:
    sql = """
    SELECT user_name AS user, COUNT(*)::bigint AS fail_count
    FROM auth_events
    WHERE (CAST(:start_ts AS TIMESTAMP) IS NULL OR ts >= :start_ts)
      AND (CAST(:end_ts AS TIMESTAMP) IS NULL OR ts <= :end_ts)
      AND (result = 'FAIL')
      AND user_name IS NOT NULL
    GROUP BY user_name
    ORDER BY fail_count DESC
    LIMIT :n
    """
    res = await db.execute(text(sql), {"start_ts": start_ts, "end_ts": end_ts, "n": n})
    rows = res.mappings().all()

    if rows:
        return [dict(row) for row in rows]

    fallback_sql = """
    SELECT user_name AS user, COUNT(*)::bigint AS fail_count
    FROM auth_events
    WHERE (CAST(:start_ts AS TIMESTAMP) IS NULL OR ts >= :start_ts)
      AND (CAST(:end_ts AS TIMESTAMP) IS NULL OR ts <= :end_ts)
      AND user_name IS NOT NULL
    GROUP BY user_name
    ORDER BY fail_count DESC
    LIMIT :n
    """
    res = await db.execute(text(fallback_sql), {"start_ts": start_ts, "end_ts": end_ts, "n": n})
    return [dict(row) for row in res.mappings().all()]


async def top_hosts(
    db: AsyncSession, start_ts: datetime | None, end_ts: datetime | None, n: int
) -> list[dict]:
    sql = """
    SELECT COALESCE(dst_host, src_host) AS host, COUNT(*)::bigint AS count
    FROM auth_events
    WHERE (CAST(:start_ts AS TIMESTAMP) IS NULL OR ts >= :start_ts)
      AND (CAST(:end_ts AS TIMESTAMP) IS NULL OR ts <= :end_ts)
      AND COALESCE(dst_host, src_host) IS NOT NULL
    GROUP BY COALESCE(dst_host, src_host)
    ORDER BY count DESC
    LIMIT :n
    """
    res = await db.execute(text(sql), {"start_ts": start_ts, "end_ts": end_ts, "n": n})
    return [dict(row) for row in res.mappings().all()]


async def user_timeline(
    db: AsyncSession,
    user: str,
    start_ts: datetime | None,
    end_ts: datetime | None,
    bucket: Literal["minute", "hour", "day"],
) -> list[dict]:
    sql = """
    SELECT date_trunc(:bucket, ts) AS bucket_start, COUNT(*)::bigint AS count
    FROM auth_events
    WHERE user_name = :user
      AND (CAST(:start_ts AS TIMESTAMP) IS NULL OR ts >= :start_ts)
      AND (CAST(:end_ts AS TIMESTAMP) IS NULL OR ts <= :end_ts)
    GROUP BY date_trunc(:bucket, ts)
    ORDER BY bucket_start ASC
    """
    res = await db.execute(
        text(sql),
        {
            "user": user,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "bucket": bucket,
        },
    )
    return [dict(row) for row in res.mappings().all()]


async def user_to_host(
    db: AsyncSession,
    start_ts: datetime | None,
    end_ts: datetime | None,
    user: str | None,
    n: int,
) -> list[dict]:
    sql = """
    SELECT user_name AS user, COALESCE(dst_host, src_host) AS host, COUNT(*)::bigint AS count
    FROM auth_events
    WHERE (CAST(:start_ts AS TIMESTAMP) IS NULL OR ts >= :start_ts)
      AND (CAST(:end_ts AS TIMESTAMP) IS NULL OR ts <= :end_ts)
      AND (CAST(:user AS TEXT) IS NULL OR user_name = :user)
      AND user_name IS NOT NULL
      AND COALESCE(dst_host, src_host) IS NOT NULL
    GROUP BY user_name, COALESCE(dst_host, src_host)
    ORDER BY count DESC
    LIMIT :n
    """
    res = await db.execute(
        text(sql), {"start_ts": start_ts, "end_ts": end_ts, "user": user, "n": n}
    )
    return [dict(row) for row in res.mappings().all()]
