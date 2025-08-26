from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


@pytest.fixture
async def created_listing_id(listing_owner_client: AsyncClient) -> str:
    """A fixture to create a listing and return its ID."""
    listing_data = {
        "type": "hotel", "name": "Updatable Hotel", "address": "123 Update St", "city": "Updateville",
        "latitude": 1.0, "longitude": 1.0, "price": 150.0, "price_unit": "per_night", "star_rating": 3
    }
    response = await listing_owner_client.post("/listings/", json=listing_data)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_update_listing_as_owner(listing_owner_client: AsyncClient, created_listing_id: str):
    """Test that the owner of a listing can successfully update it."""
    update_data = {"name": "Renovated Hotel", "price": 175.0}
    response = await listing_owner_client.patch(f"/listings/{created_listing_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Renovated Hotel"
    assert data["price"] == 175.0
    assert data["star_rating"] == 3  # Verify non-updated fields remain the same


@pytest.mark.asyncio
async def test_update_listing_as_non_owner(reviewer_client: AsyncClient, created_listing_id: str):
    """Test that a user who is not the owner cannot update the listing."""
    update_data = {"name": "Malicious Update"}
    response = await reviewer_client.patch(f"/listings/{created_listing_id}", json=update_data)

    assert response.status_code == 403
    assert "permission to modify" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_listing_with_invalid_data(listing_owner_client: AsyncClient, created_listing_id: str):
    """Test that updating a listing with invalid data fails validation."""
    update_data = {"price": -50}  # Invalid price
    response = await listing_owner_client.patch(f"/listings/{created_listing_id}", json=update_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_listing_as_non_owner(reviewer_client: AsyncClient, created_listing_id: str):
    """Test that a user who is not the owner cannot delete the listing."""
    response = await reviewer_client.delete(f"/listings/{created_listing_id}")
    assert response.status_code == 403
    assert "permission to modify" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_listing_as_owner(listing_owner_client: AsyncClient, created_listing_id: str, monkeypatch):
    """Test that the owner of a listing can successfully delete it."""
    # Mock the cloudinary functions
    mock_upload = AsyncMock(return_value={"secure_url": "https://mock.cloudinary.com/image.jpg",
                                          "public_id": f"listings/{created_listing_id}/image"})
    mock_delete_folder = AsyncMock()
    monkeypatch.setattr("src.cloudinary.utils.upload_image", mock_upload)
    monkeypatch.setattr("src.cloudinary.utils.delete_folder", mock_delete_folder)

    # Upload an image to the listing so we can verify its folder gets deleted
    files = {"file": ("image.jpg", b"content", "image/jpeg")}
    await listing_owner_client.post(f"/listings/{created_listing_id}/images", files=files)

    # Delete the listing
    delete_response = await listing_owner_client.delete(f"/listings/{created_listing_id}")
    assert delete_response.status_code == 204

    # Verify the Cloudinary folder deletion was called with the correct path
    mock_delete_folder.assert_called_once_with(f"listings/{created_listing_id}")

    # Verify the listing is gone
    get_response = await listing_owner_client.get(f"/listings/{created_listing_id}")
    assert get_response.status_code == 404
