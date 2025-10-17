"""
Tests for chat endpoints.
"""
import pytest
from httpx import AsyncClient
import json


@pytest.mark.asyncio
async def test_chat_askatt_streaming(authenticated_client: AsyncClient):
    """Test AskAT&T chat with streaming."""
    response = await authenticated_client.post(
        "/api/v1/chat/askatt",
        json={"message": "Hello, how are you?"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Read streaming response
    content = response.text
    assert "data:" in content
    assert '"type":"token"' in content
    assert '"type":"end"' in content


@pytest.mark.asyncio
async def test_chat_askatt_no_auth(client: AsyncClient):
    """Test AskAT&T chat without authentication."""
    response = await client.post(
        "/api/v1/chat/askatt",
        json={"message": "Hello"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_askdocs_no_config(authenticated_client: AsyncClient):
    """Test AskDocs chat without configuration_id."""
    response = await authenticated_client.post(
        "/api/v1/chat/askdocs",
        json={"message": "Hello"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_configurations(authenticated_client: AsyncClient):
    """Test get configurations endpoint."""
    response = await authenticated_client.get("/api/v1/chat/configurations")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_conversations(authenticated_client: AsyncClient):
    """Test get conversations endpoint."""
    response = await authenticated_client.get("/api/v1/chat/conversations")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
