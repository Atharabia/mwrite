import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-32-chars-minimum!")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.com")
os.environ.setdefault("ADMIN_PASSWORD", "TestPass123!")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="session")
async def engine():
    test_engine = create_async_engine(TEST_DB_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db(engine):
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="session")
async def client():
    from app import app as fastapi_app
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as c:
        yield c


def make_token(email: str, roles: list[str]) -> str:
    from app.dependencies.admin_auth import WriterAuth
    return WriterAuth.create_token(
        {"sub": email, "roles": roles},
        expires_minutes=30
    )
