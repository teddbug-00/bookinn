import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_amenity_as_admin(authenticated_admin_client: AsyncClient):
    """Test that an admin can create a new amenity."""
    amenity_data = {"name": "Swimming Pool", "icon_url": "https://example.com/pool.png"}
    response = await authenticated_admin_client.post("/admin/amenities", json=amenity_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Swimming Pool"
    assert response.json()["icon_url"] == "https://example.com/pool.png"


@pytest.mark.asyncio
async def test_create_amenity_as_regular_user(authenticated_client: AsyncClient):
    """Test that a regular user cannot create a new amenity."""
    amenity_data = {"name": "Forbidden Amenity", "icon_url": "https://example.com/pool.png"}
    response = await authenticated_client.post("/admin/amenities", json=amenity_data)
    assert response.status_code == 403
    assert "permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_duplicate_amenity(authenticated_admin_client: AsyncClient):
    """Test that creating an amenity with a duplicate name fails."""
    amenity_data = {"name": "Free WiFi", "icon_url": "https://example.com/pool.png"}
    response1 = await authenticated_admin_client.post("/admin/amenities", json=amenity_data)
    assert response1.status_code == 201
    response2 = await authenticated_admin_client.post("/admin/amenities", json=amenity_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_get_all_amenities(client: AsyncClient, authenticated_admin_client: AsyncClient):
    """Test that anyone can retrieve a list of all amenities."""
    # Create an amenity first
    await authenticated_admin_client.post("/admin/amenities", json={"name": "Parking"})
    # Fetch as an unauthenticated client
    response = await client.get("/amenities/")
    assert response.status_code == 200
    amenities = response.json()
    assert isinstance(amenities, list)
    assert len(amenities) > 0
    assert any(amenity["name"] == "Parking" for amenity in amenities)


@pytest.mark.asyncio
async def test_update_amenity_as_admin(authenticated_admin_client: AsyncClient):
    """Test that an admin can update an amenity."""
    create_response = await authenticated_admin_client.post("/admin/amenities", json={"name": "Old Name",
                                                                                "icon_url": "https://example.com/old.png"})
    amenity_id = create_response.json()["id"]
    update_response = await authenticated_admin_client.patch(f"/admin/amenities/{amenity_id}", json={"name": "New Name",
                                                                                               "icon_url": "https://example.com/new.png"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "New Name"
    assert update_response.json()["icon_url"] == "https://example.com/new.png"


@pytest.mark.asyncio
async def test_delete_amenity_as_admin(authenticated_admin_client: AsyncClient):
    """Test that an admin can delete an amenity."""
    create_response = await authenticated_admin_client.post("/admin/amenities", json={"name": "To Be Deleted",
                                                                                "icon_url": "https://example.com/delete.png"})
    amenity_id = create_response.json()["id"]
    delete_response = await authenticated_admin_client.delete(f"/admin/amenities/{amenity_id}")
    assert delete_response.status_code == 204
    # Verify it's gone
    get_response = await authenticated_admin_client.get("/amenities/")
    assert not any(amenity["id"] == amenity_id for amenity in get_response.json())
