from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


@pytest.fixture
async def created_listing_id(listing_owner_client: AsyncClient) -> str:
    """A fixture to create a listing and return its ID."""
    listing_data = {
        "type": "hotel", "name": "Hotel with Images", "address": "123 Image St", "city": "Imageville",
        "latitude": 1.0, "longitude": 1.0, "price": 150.0, "price_unit": "per_night", "star_rating": 3
    }
    response = await listing_owner_client.post("/listings/", json=listing_data)
    return response.json()["id"]


@pytest.mark.asyncio
async def test_upload_image_as_owner(listing_owner_client: AsyncClient, created_listing_id: str, monkeypatch):
    """Test that the owner can upload an image to their listing."""
    # Mock the cloudinary upload function to avoid real network calls
    mock_upload = AsyncMock(return_value={"secure_url": "https://mock.cloudinary.com/test_image.jpg"})
    monkeypatch.setattr("src.cloudinary.utils.upload_image", mock_upload)

    file_content = b"test image content"
    files = {"file": ("test_image.jpg", file_content, "image/jpeg")}
    response = await listing_owner_client.post(f"/listings/{created_listing_id}/images", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://mock.cloudinary.com/test_image.jpg"
    assert data["is_thumbnail"] is False
    mock_upload.assert_called_once()


@pytest.mark.asyncio
async def test_upload_image_as_non_owner(reviewer_client: AsyncClient, created_listing_id: str):
    """Test that a non-owner cannot upload an image to a listing."""
    file_content = b"malicious content"
    files = {"file": ("hacker.jpg", file_content, "image/jpeg")}
    response = await reviewer_client.post(f"/listings/{created_listing_id}/images", files=files)

    assert response.status_code == 403
    assert "permission to modify" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_thumbnail_twice(listing_owner_client: AsyncClient, created_listing_id: str, monkeypatch):
    """Test that a user cannot set a second thumbnail if one already exists."""
    # Mock the cloudinary upload function
    mock_upload = AsyncMock()
    monkeypatch.setattr("src.cloudinary.utils.upload_image", mock_upload)

    # Upload the first thumbnail
    mock_upload.return_value = {"secure_url": "https://mock.cloudinary.com/thumbnail1.jpg"}
    files = {"file": ("thumbnail1.jpg", b"thumb1", "image/jpeg")}
    data = {"is_thumbnail": "true"}
    await listing_owner_client.post(f"/listings/{created_listing_id}/images", files=files, data=data)

    # Attempt to upload a second thumbnail
    mock_upload.return_value = {"secure_url": "https://mock.cloudinary.com/thumbnail2.jpg"}
    files_2 = {"file": ("thumbnail2.jpg", b"thumb2", "image/jpeg")}
    response = await listing_owner_client.post(f"/listings/{created_listing_id}/images", files=files_2, data=data)

    assert response.status_code == 409
    assert "thumbnail for this listing already exists" in response.json()["detail"]
