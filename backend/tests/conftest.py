"""
Pytest configuration and fixtures for testing.
"""
import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base
from app.api.deps import get_db
from app.core.security import get_password_hash
from app.models.user import User, Role

# Test database URL (use in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_factory = async_sessionmaker(
        db_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create test user with USER role."""
    # Create USER role
    user_role = Role(name="USER", description="Test user role")
    db_session.add(user_role)
    await db_session.flush()

    # Create test user
    user = User(
        attid="testuser",
        email="test@example.com",
        password_hash=get_password_hash("Test123!"),
        full_name="Test User",
        is_active=True
    )
    user.roles.append(user_role)

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    """Create test admin user with ADMIN role."""
    # Create ADMIN role
    admin_role = Role(name="ADMIN", description="Test admin role")
    db_session.add(admin_role)
    await db_session.flush()

    # Create admin user
    admin = User(
        attid="admin",
        email="admin@example.com",
        password_hash=get_password_hash("Admin123!"),
        full_name="Admin User",
        is_active=True
    )
    admin.roles.append(admin_role)

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    return admin


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authenticated_client(
    client: AsyncClient,
    test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated HTTP client with test user token."""
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        json={"attid": "testuser", "password": "Test123!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Set authorization header
    client.headers["Authorization"] = f"Bearer {token}"

    yield client


@pytest.fixture(scope="function")
async def admin_client(
    client: AsyncClient,
    admin_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated HTTP client with admin user token."""
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        json={"attid": "admin", "password": "Admin123!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Set authorization header
    client.headers["Authorization"] = f"Bearer {token}"

    yield client
