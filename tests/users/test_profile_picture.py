from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_profile_picture(authenticated_client: AsyncClient, monkeypatch):
    """Test that an authenticated user can upload a profile picture."""
    # Mock the Cloudinary upload function
    mock_upload = AsyncMock(return_value={
        "secure_url": "https://mock.cloudinary.com/profile.jpg",
        "public_id": "profile_pictures/some_user_id/profile"
    })
    monkeypatch.setattr("src.cloudinary.utils.upload_image", mock_upload)

    file_content = b"fake image data"
    files = {"file": ("profile.jpg", file_content, "image/jpeg")}

    response = await authenticated_client.post("/users/profile/picture", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["profile_picture_url"] == "https://mock.cloudinary.com/profile.jpg"
    mock_upload.assert_called_once()


@pytest.mark.asyncio
async def test_replace_profile_picture(authenticated_client: AsyncClient, monkeypatch):
    """Test that uploading a new picture deletes the old one."""
    # Mock the Cloudinary upload and delete functions
    mock_upload = AsyncMock()
    mock_delete = AsyncMock()
    monkeypatch.setattr("src.cloudinary.utils.upload_image", mock_upload)
    monkeypatch.setattr("src.cloudinary.utils.delete_image", mock_delete)

    # 1. Upload the first picture
    mock_upload.return_value = {
        "secure_url": "https://mock.cloudinary.com/old_profile.jpg",
        "public_id": "profile_pictures/some_user_id/old_profile"
    }
    files1 = {"file": ("old_profile.jpg", b"old image", "image/jpeg")}
    await authenticated_client.post("/users/profile/picture", files=files1)

    # 2. Upload the second picture
    mock_upload.return_value = {
        "secure_url": "https://mock.cloudinary.com/new_profile.jpg",
        "public_id": "profile_pictures/some_user_id/new_profile"
    }
    files2 = {"file": ("new_profile.jpg", b"new image", "image/jpeg")}
    response = await authenticated_client.post("/users/profile/picture", files=files2)

    assert response.status_code == 200
    assert response.json()["profile_picture_url"] == "https://mock.cloudinary.com/new_profile.jpg"

    # 3. Verify the old image was deleted
    mock_delete.assert_called_once_with("profile_pictures/some_user_id/old_profile")
