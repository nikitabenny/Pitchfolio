import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Base

BOOTSTRAP = {
    "events": [{"id": 1, "is_current": False}, {"id": 2, "is_current": True}],
    "elements": [
        {"id": 101, "now_cost": 55},
        {"id": 102, "now_cost": 60},
        {"id": 103, "now_cost": 45},
    ],
}


@pytest_asyncio.fixture
async def db_session():
    #DATABASE_URL is never actually connected to here - sqlite in-memory stands in for it
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def fake_client():
    #per-test mutable responses so a test can set fake_client.mock_responses["transfers"] = [...] etc.
    responses = {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/bootstrap-static/"):
            return httpx.Response(200, json=BOOTSTRAP)
        if "/transfers/" in path:
            return httpx.Response(200, json=responses.get("transfers", []))
        if path.endswith("/entry/999/"):
            return httpx.Response(200, json=responses.get("myinfo", {}))
        if "/event/" in path and "/picks/" in path:
            return httpx.Response(200, json=responses.get("picks", {"picks": []}))
        raise AssertionError(f"unexpected request path: {path}")

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://fantasy.premierleague.com/api/",
    )
    client.mock_responses = responses
    return client
