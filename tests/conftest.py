from typing import AsyncGenerator

import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

from src.main import app
from src.database import Base, get_db_session

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Provides an asynchronous SQLAlchemy engine for the test database.
    Scoped to the session to create the database once.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous SQLAlchemy session for each test function.
    Rolls back transactions after each test to ensure isolation.
    """
    async_session = async_sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
        # Rollback the transaction after each test to clean up
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an asynchronous HTTP client for testing FastAPI endpoints.
    Overrides the database dependency to use the test session.
    """
    # Override the get_db_session dependency to use the test session
    app.dependency_overrides[get_db_session] = lambda: test_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    """
    Provides an authenticated client with a valid JWT token set in the headers.
    """
    user_data = {
        "email": "auth@example.com",
        "password": "authpassword",
        "name": "Auth User",
        "date_of_birth": "1995-01-01"
    }
    await client.post("/users/", json=user_data)

    login_response = await client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
