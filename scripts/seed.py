import argparse
import csv
import json
import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import Json, execute_values


def to_psycopg_dsn(raw_url: str) -> str:
    for prefix in ["postgresql+psycopg2://", "postgresql+asyncpg://"]:
        if raw_url.startswith(prefix):
            return raw_url.replace(prefix, "postgresql://", 1)
    return raw_url


def parse_timestamp(value: str) -> datetime:
    if "." in value:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def to_result(login_successful: str | None) -> str | None:
    if login_successful is None:
        return None
    v = login_successful.strip().lower()
    if v == "true":
        return "SUCCESS"
    if v == "false":
        return "FAIL"
    return None


def to_row(raw_row: dict) -> tuple:
    ts = parse_timestamp(raw_row["Login Timestamp"])
    user_name = raw_row.get("User ID")
    src_host = raw_row.get("IP Address")
    dst_host = raw_row.get("Country") or raw_row.get("ASN")
    auth_type = raw_row.get("Browser Name and Version")
    result = to_result(raw_row.get("Login Successful"))
    return (ts, user_name, src_host, dst_host, auth_type, result, Json(raw_row))


def truncate_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE auth_events RESTART IDENTITY")
    conn.commit()


def seed(conn, csv_path: str, max_rows: int | None = None, batch_size: int = 5000) -> int:
    insert_sql = """
    INSERT INTO auth_events (ts, user_name, src_host, dst_host, auth_type, result, raw)
    VALUES %s
    """
    total = 0
    batch = []

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append(to_row(row))
            if len(batch) >= batch_size:
                with conn.cursor() as cur:
                    execute_values(cur, insert_sql, batch)
                conn.commit()
                total += len(batch)
                batch.clear()
                print(f"Inserted: {total}")

            if max_rows is not None and total + len(batch) >= max_rows:
                break

    if batch:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, batch)
        conn.commit()
        total += len(batch)
        print(f"Inserted: {total}")

    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed auth_events from CSV.")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default="rba-dataset-100k.csv",
        help="Path to CSV file",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional max number of rows to import",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate table before import",
    )
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL must be set before importing data.")
    dsn = to_psycopg_dsn(db_url)
    parsed = urlparse(dsn)
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ValueError("DATABASE_URL must be a PostgreSQL URL")

    conn = psycopg2.connect(dsn)
    try:
        if args.truncate:
            truncate_table(conn)
        inserted = seed(conn, args.csv_path, args.max_rows)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM auth_events")
            db_count = cur.fetchone()[0]
        print(json.dumps({"inserted": inserted, "db_count": db_count}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
