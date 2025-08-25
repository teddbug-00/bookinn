import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient):
    """Test that a registered user can log in and receive tokens."""
    # First, register a user
    await client.post("/users/", json={
        "email": "login@example.com",
        "password": "loginpassword",
        "name": "Login User",
        "date_of_birth": "1990-05-10"
    })

    # Then, attempt to log in
    response = await client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "loginpassword"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_wrong_password(client: AsyncClient):
    """Test that login fails with an incorrect password."""
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword",
        "name": "Wrong Pass User",
        "date_of_birth": "1999-01-01"
    }
    await client.post("/users/", json=user_data)

    response = await client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": "thisiswrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test that a valid refresh token can be used to get a new access token."""
    # First, register and log in a user to get a refresh token
    await client.post("/users/",
                      json={"email": "refresh@example.com", "password": "refreshpassword", "name": "Refresh User",
                            "date_of_birth": "1998-01-01"})
    login_response = await client.post("/auth/login",
                                       json={"email": "refresh@example.com", "password": "refreshpassword"})
    tokens = login_response.json()
    refresh_token = tokens["refresh_token"]
    original_access_token = tokens["access_token"]

    # Introduce a small delay to ensure the new token's 'exp' claim is different
    await asyncio.sleep(1)

    # Use the refresh token to get new tokens
    refresh_response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["access_token"] != original_access_token
