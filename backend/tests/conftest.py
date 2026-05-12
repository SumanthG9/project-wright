import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.core.config import settings
from backend.db.session import get_db
from backend.main import app
from backend.models import Base


# ── Single event loop for the entire test session ─────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Shared event loop — prevents 'Future attached to a different loop' errors."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Test database URL ─────────────────────────────────────────────────────────
TEST_DATABASE_URL = settings.database_url.replace(
    "/project_wright", "/project_wright_test"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


# ── Dependency override ───────────────────────────────────────────────────────
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ── Session-scoped: create all tables once, drop after all tests ──────────────
@pytest.fixture(scope="session", autouse=True)
async def create_test_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── Function-scoped: truncate all tables after every single test ──────────────
@pytest.fixture(autouse=True)
async def clean_tables():
    yield
    async with test_engine.begin() as conn:
        await conn.exec_driver_sql(
            "TRUNCATE TABLE hitl_checkpoints, agent_runs, drafts, projects, users "
            "RESTART IDENTITY CASCADE"
        )


# ── HTTP client ───────────────────────────────────────────────────────────────
@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Registered user + auth headers ───────────────────────────────────────────
@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "secret123",
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def auth_headers(registered_user: dict) -> dict:
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
