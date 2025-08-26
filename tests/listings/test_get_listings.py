import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.images.models import Image


@pytest.mark.asyncio
async def test_get_all_listings_empty(client: AsyncClient):
    """Test retrieving all listings when none have been created."""
    response = await client.get("/listings/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_listings_with_data(
        client: AsyncClient,
        listing_owner_client: AsyncClient,
        reviewer_client: AsyncClient,
        test_session: AsyncSession
):
    """Test retrieving all listings when multiple exist."""
    # Create a hotel
    hotel_data = {
        "type": "hotel", "name": "Alpha Hotel", "address": "123 Alpha St", "city": "Alphaville",
        "latitude": 1.0, "longitude": 1.0, "price": 100.0, "price_unit": "per_night", "star_rating": 4
    }
    hotel_res = await listing_owner_client.post("/listings/", json=hotel_data)
    hotel_id = uuid.UUID(hotel_res.json()["id"])

    # Add an image to the hotel to test the thumbnail
    image = Image(url="https://example.com/image.jpg", is_thumbnail=True, listing_id=hotel_id)
    test_session.add(image)
    await test_session.commit()

    # Add a review for the hotel as a reviewer
    review_data = {"rating": 5, "comment": "Excellent stay!"}
    await reviewer_client.post(f"/listings/{hotel_id}/reviews", json=review_data)


    # Create an apartment
    apartment_data = {
        "type": "apartment", "name": "Beta Apartments", "address": "456 Beta Ave", "city": "Betatown",
        "latitude": 2.0, "longitude": 2.0, "price": 1500.0, "price_unit": "per_month",
        "number_of_bedrooms": 2, "number_of_bathrooms": 1, "max_guests": 4
    }
    await listing_owner_client.post("/listings/", json=apartment_data)

    # Act
    response = await client.get("/listings/")

    # Assert
    assert response.status_code == 200
    listings = response.json()
    assert len(listings) == 2
    assert {listing['name'] for listing in listings} == {"Alpha Hotel", "Beta Apartments"}

    # Verify the structure of the summary response
    hotel_summary = next((l for l in listings if l["name"] == "Alpha Hotel"), None)
    assert hotel_summary is not None
    assert hotel_summary["address"] == "123 Alpha St"
    assert hotel_summary["thumbnail_url"] == "https://example.com/hotel.jpg"
    assert hotel_summary["total_reviews"] == 1
    assert hotel_summary["average_rating"] == 5.0
    assert "number_of_bedrooms" not in hotel_summary  # Verify it's the summary view
