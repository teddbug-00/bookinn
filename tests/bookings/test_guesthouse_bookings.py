import datetime

import pytest
from httpx import AsyncClient


@pytest.fixture
async def created_guesthouse_id(listing_owner_client: AsyncClient) -> str:
    """A fixture to create a guesthouse listing and return its ID."""
    listing_data = {
        "type": "guesthouse",
        "name": "The Cozy Guesthouse",
        "address": "123 Guest St",
        "city": "Guestville",
        "latitude": 1.0,
        "longitude": 1.0,
        "price": 120.0,
        "price_unit": "per_night",
        "number_of_rooms": 3,
        "host_on_site": True
    }
    response = await listing_owner_client.post("/listings/", json=listing_data)
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_guesthouse_booking_success(reviewer_client: AsyncClient, created_guesthouse_id: str):
    """Test successfully booking rooms in a guesthouse."""
    today = datetime.date.today()
    check_in = today + datetime.timedelta(days=1)
    check_out = today + datetime.timedelta(days=3)  # 2 nights

    booking_data = {
        "type": "guesthouse",
        "listing_id": created_guesthouse_id,
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat(),
        "number_of_rooms": 2
    }

    response = await reviewer_client.post("/bookings/", json=booking_data)

    assert response.status_code == 201
    data = response.json()
    assert data["total_price"] == 480.0  # 2 rooms * 2 nights * 120 price
    assert data["number_of_rooms_booked"] == 2


@pytest.mark.asyncio
async def test_create_booking_not_enough_rooms(reviewer_client: AsyncClient, created_guesthouse_id: str):
    """Test that a booking fails if not enough rooms are available."""
    today = datetime.date.today()
    check_in = today + datetime.timedelta(days=10)
    check_out = today + datetime.timedelta(days=12)

    # Book 2 out of 3 rooms
    await reviewer_client.post(f"/bookings/", json={
        "type": "guesthouse", "listing_id": created_guesthouse_id, "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat(), "number_of_rooms": 2
    })

    # Attempt to book 2 more rooms for the same dates (only 1 is left)
    response = await reviewer_client.post(f"/bookings/", json={
        "type": "guesthouse", "listing_id": created_guesthouse_id, "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat(), "number_of_rooms": 2
    })

    assert response.status_code == 409
    assert "Not enough rooms available" in response.json()["detail"]
