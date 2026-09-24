import os
from datetime import datetime

os.environ["DATABASE_URL"] = "postgresql+asyncpg://localhost/test"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok(monkeypatch):
    async def ping_db():
        return True

    monkeypatch.setattr("app.routers.health.ping_db", ping_db)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["db"] == "ok"


def test_health_degraded_when_database_fails(monkeypatch):
    async def ping_db():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr("app.routers.health.ping_db", ping_db)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["db"] == "error"


def test_stats(monkeypatch):
    async def get_stats(_db):
        return {
            "count": 100,
            "min_ts": datetime(2020, 2, 3, 12, 0, 0),
            "max_ts": datetime(2020, 2, 4, 12, 0, 0),
        }

    monkeypatch.setattr("app.repository.get_stats", get_stats)
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    assert response.json()["count"] == 100


def test_events(monkeypatch):
    async def search_events(**_kwargs):
        return [{
            "id": 1,
            "ts": datetime(2020, 2, 3, 12, 0, 0),
            "user_name": "demo-user",
            "src_host": "example.invalid",
            "dst_host": "example",
            "auth_type": "Browser",
            "result": "FAIL",
        }]

    monkeypatch.setattr("app.repository.search_events", search_events)
    response = client.get("/api/v1/events?limit=10&offset=0")
    assert response.status_code == 200
    assert response.json()[0]["user_name"] == "demo-user"
def test_events_require_cursor_pair():
    response = client.get("/api/v1/events?cursor_id=1")
    assert response.status_code == 422


def test_top_users(monkeypatch):
    async def top_users(*_args):
        return [{"user": "demo-user", "fail_count": 3}]

    monkeypatch.setattr("app.repository.top_users_by_failures", top_users)
    response = client.get("/api/v1/suspicious/top-users?n=5")
    assert response.status_code == 200
    assert response.json()[0]["fail_count"] == 3


def test_top_hosts(monkeypatch):
    async def top_hosts(*_args):
        return [{"host": "example", "count": 7}]

    monkeypatch.setattr("app.repository.top_hosts", top_hosts)
    response = client.get("/api/v1/suspicious/top-hosts?n=5")
    assert response.status_code == 200
    assert response.json()[0]["host"] == "example"


def test_user_timeline(monkeypatch):
    async def user_timeline(*_args):
        return [{"bucket_start": datetime(2020, 2, 3, 12, 0, 0), "count": 4}]

    monkeypatch.setattr("app.repository.user_timeline", user_timeline)
    response = client.get(
        "/api/v1/suspicious/user-timeline?user=demo-user&bucket=hour"
    )
    assert response.status_code == 200
    assert response.json()[0]["count"] == 4
def test_user_to_host(monkeypatch):
    async def user_to_host(*_args):
        return [{"user": "demo-user", "host": "example", "count": 2}]

    monkeypatch.setattr("app.repository.user_to_host", user_to_host)
    response = client.get("/api/v1/aggregate/user-to-host?n=10")
    assert response.status_code == 200
    assert response.json()[0]["host"] == "example"
