import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_session: AsyncSession):
    """Test that a new user can be registered successfully."""
    user_data = {
        "email": "test@example.com",
        "password": "securepassword",
        "name": "Test User",
        "date_of_birth": "2000-01-01"
    }
    response = await client.post("/users/", json=user_data)

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert response.json()["name"] == "Test User"
    assert response.json()["date_of_birth"] == "2000-01-01"
    assert "id" in response.json()

    # Verify user is in the database
    user_id = uuid.UUID(response.json()["id"])
    user = await test_session.get(User, user_id)
    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_profile(authenticated_client: AsyncClient):
    """Test retrieving the profile of the currently authenticated user."""
    response = await authenticated_client.get("/users/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "auth@example.com"
    assert data["name"] == "Auth User"


@pytest.mark.asyncio
async def test_update_current_user_profile(authenticated_client: AsyncClient, test_session: AsyncSession):
    """Test updating the profile of the currently authenticated user."""
    update_data = {"name": "Updated Name", "profile_picture_url": "http://example.com/pic.jpg"}
    response = await authenticated_client.patch("/users/profile", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["profile_picture_url"] == "http://example.com/pic.jpg"
    assert data["email"] == "auth@example.com"  # Email should not change

    # Verify in DB
    user = await test_session.get(User, uuid.UUID(data["id"]))
    assert user.name == "Updated Name"
    assert user.profile_picture_url == "http://example.com/pic.jpg"


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    """Test that registering a user with a duplicate email fails."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "name": "First User",
        "date_of_birth": "2000-01-01"
    }
    # First registration should succeed
    response1 = await client.post("/users/", json=user_data)
    assert response1.status_code == 201

    # Second registration with the same email should fail
    user_data["name"] = "Second User"  # change other data
    response2 = await client.post("/users/", json=user_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_access_protected_route_with_invalid_token(client: AsyncClient):
    """Test that accessing a protected route with an invalid token fails."""
    client.headers["Authorization"] = "Bearer thisisnotavalidtoken"
    response = await client.get("/users/profile")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."
