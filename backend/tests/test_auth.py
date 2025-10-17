"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test successful user signup."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "attid": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["attid"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "USER" in data["roles"]


@pytest.mark.asyncio
async def test_signup_duplicate_attid(client: AsyncClient, test_user):
    """Test signup with duplicate AT&T ID."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "attid": "testuser",  # Already exists
            "email": "different@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
    )

    assert response.status_code == 422
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient):
    """Test signup with weak password."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "attid": "newuser",
            "email": "newuser@example.com",
            "password": "weak",  # Too weak
            "full_name": "New User"
        }
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "attid": "testuser",
            "password": "Test123!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["attid"] == "testuser"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "attid": "testuser",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client: AsyncClient, test_user):
    """Test get current user endpoint."""
    response = await authenticated_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["attid"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test get current user without token."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
