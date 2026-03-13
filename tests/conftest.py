"""Shared test fixtures for the e-commerce API test suite."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.main import app
from ecommerce.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncEngine:
    """Create a test database engine using in-memory SQLite."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def session(test_engine: AsyncEngine):
    """Provide a clean database session for each test.

    Rolls back all changes after each test to ensure isolation.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(test_engine) as session:
        async def override_get_session():
            yield session

        app.dependency_overrides[get_session] = override_get_session
        yield session

    # Clean all tables after each test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Provide an async HTTP client for testing the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
