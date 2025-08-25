import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_listing_unauthenticated(client: AsyncClient):
    """Test that an unauthenticated user cannot create a listing."""
    listing_data = {
        "type": "hotel",
        "name": "Test Hotel",
        "address": "123 Test St",
        "city": "Testville",
        "latitude": 1.0,
        "longitude": 1.0,
        "price": 100.0,
        "price_unit": "per_night",
        "star_rating": 5,
    }
    response = await client.post("/listings/", json=listing_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_hotel_listing_authenticated(
        authenticated_client: AsyncClient, authenticated_admin_client: AsyncClient
):
    """Test that an authenticated user can create a hotel listing with amenities."""
    # First, create some amenities as an admin to ensure they exist
    amenity1_res = await authenticated_admin_client.post("/amenities", json={"name": "Pool"})
    amenity2_res = await authenticated_admin_client.post("/amenities", json={"name": "Gym"})
    amenity1_id = amenity1_res.json()["id"]
    amenity2_id = amenity2_res.json()["id"]

    listing_data = {
        "type": "hotel",
        "name": "Grand Test Hotel",
        "description": "A grand hotel for testing.",
        "address": "456 Grand Ave",
        "city": "Testopolis",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "price": 250.50,
        "price_unit": "per_night",
        "star_rating": 5,
        "amenity_ids": [amenity1_id, amenity2_id],
    }

    response = await authenticated_client.post("/listings/", json=listing_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Grand Test Hotel"
    assert data["type"] == "hotel"
    assert data["star_rating"] == 5
    assert len(data["amenities"]) == 2
    assert {a["id"] for a in data["amenities"]} == {amenity1_id, amenity2_id}


@pytest.mark.asyncio
async def test_create_apartment_listing_authenticated(authenticated_client: AsyncClient):
    """Test that an authenticated user can create an apartment listing."""
    listing_data = {
        "type": "apartment",
        "name": "Modern Downtown Loft",
        "description": "A stylish loft in the heart of the city.",
        "address": "789 Urban St",
        "city": "Metroville",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "price": 3000.00,
        "price_unit": "per_month",
        "number_of_bedrooms": 1,
        "number_of_bathrooms": 1,
        "max_guests": 2,
    }
    response = await authenticated_client.post("/listings/", json=listing_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Modern Downtown Loft"
    assert data["type"] == "apartment"
    assert data["number_of_bedrooms"] == 1


@pytest.mark.asyncio
async def test_create_listing_with_invalid_amenity(authenticated_client: AsyncClient):
    """Test that creating a listing with a non-existent amenity ID fails."""
    listing_data = {
        "type": "apartment", "name": "Test Apartment", "address": "789 Apt Way", "city": "Testburg",
        "latitude": 2.0, "longitude": 2.0, "price": 1200.0, "price_unit": "per_month",
        "number_of_bedrooms": 2, "number_of_bathrooms": 1, "max_guests": 4,
        "amenity_ids": [str(uuid.uuid4())],
    }
    response = await authenticated_client.post("/listings/", json=listing_data)
    assert response.status_code == 400
    assert "invalid or not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_guesthouse_listing_authenticated(authenticated_client: AsyncClient):
    """Test that an authenticated user can create a guesthouse listing."""
    listing_data = {
        "type": "guesthouse",
        "name": "Cozy Guesthouse",
        "description": "A cozy guesthouse for a relaxing stay.",
        "address": "1 Cozy Lane",
        "city": "Comfortown",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "price": 120.00,
        "price_unit": "per_night",
        "number_of_rooms": 3,
        "host_on_site": True,
    }

    response = await authenticated_client.post("/listings/", json=listing_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Cozy Guesthouse"
    assert data["type"] == "guesthouse"
    assert data["number_of_rooms"] == 3


@pytest.mark.asyncio
async def test_create_hostel_listing_authenticated(authenticated_client: AsyncClient):
    """Test that an authenticated user can create a hostel listing."""
    listing_data = {
        "type": "hostel",
        "name": "Backpacker's Hub",
        "description": "A friendly hostel for travelers.",
        "address": "101 Traveler Rd",
        "city": "Adventure City",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "price": 25.00,
        "price_unit": "per_night",
        "dorm_bed_count": 8,
        "private_room_count": 2,
    }

    response = await authenticated_client.post("/listings/", json=listing_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Backpacker's Hub"
    assert data["type"] == "hostel"
    assert data["dorm_bed_count"] == 8
    assert data["private_room_count"] == 2
