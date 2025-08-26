import datetime

import pytest
from httpx import AsyncClient


@pytest.fixture
async def created_apartment_id(listing_owner_client: AsyncClient) -> str:
    """A fixture to create an apartment listing and return its ID."""
    listing_data = {
        "type": "apartment",
        "name": "The Downtown Apartment",
        "address": "123 Main St",
        "city": "Metropolis",
        "latitude": 1.0,
        "longitude": 1.0,
        "price": 1500.0,
        "price_unit": "per_month",
        "number_of_bedrooms": 2,
        "number_of_bathrooms": 1,
        "max_guests": 4,
        "min_lease_months": 3
    }
    response = await listing_owner_client.post("/listings/", json=listing_data)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_apartment_booking_success(reviewer_client: AsyncClient, created_apartment_id: str):
    """Test successfully booking an apartment for a valid lease period."""
    today = datetime.date.today()
    check_in = today + datetime.timedelta(days=5)

    booking_data = {
        "listing_id": created_apartment_id,
        "check_in_date": check_in.isoformat(),
        "number_of_months": 4
    }

    response = await reviewer_client.post("/bookings/apartment", json=booking_data)

    assert response.status_code == 201
    data = response.json()
    assert data["total_price"] == 6000.0  # 4 months * 1500 price
    assert data["listing_id"] == created_apartment_id


@pytest.mark.asyncio
async def test_create_booking_for_unavailable_dates(reviewer_client: AsyncClient, created_apartment_id: str):
    """Test that a booking fails if the dates are already taken."""
    today = datetime.date.today()
    check_in = today + datetime.timedelta(days=20)

    booking_data = {"listing_id": created_apartment_id, "check_in_date": check_in.isoformat(), "number_of_months": 3}

    # First booking should succeed
    await reviewer_client.post("/bookings/apartment", json=booking_data)

    # Attempt to book overlapping dates again
    response = await reviewer_client.post("/bookings/apartment", json=booking_data)

    assert response.status_code == 409
    assert "dates are not available" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_booking_below_min_lease(reviewer_client: AsyncClient, created_apartment_id: str):
    """Test that a booking fails if the lease period is too short."""
    today = datetime.date.today()
    check_in = today + datetime.timedelta(days=40)

    booking_data = {"listing_id": created_apartment_id, "check_in_date": check_in.isoformat(), "number_of_months": 2}
    response = await reviewer_client.post("/bookings/apartment", json=booking_data)

    assert response.status_code == 400
    assert "minimum lease period" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_my_bookings(reviewer_client: AsyncClient, created_apartment_id: str):
    """Test retrieving all bookings for the authenticated user."""
    # 1. Create a booking
    booking_data = {
        "listing_id": created_apartment_id,
        "check_in_date": (datetime.date.today() + datetime.timedelta(days=60)).isoformat(),
        "number_of_months": 3
    }
    await reviewer_client.post("/bookings/apartment", json=booking_data)

    # 2. Fetch the bookings for that user
    response = await reviewer_client.get("/bookings/my-bookings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["listing_id"] == created_apartment_id
