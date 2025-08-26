import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.images.models import Image


@pytest.mark.asyncio
async def test_get_all_listings_empty(client: AsyncClient):
    """Test retrieving all listings when none have been created."""
    response = await client.get("/listings")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


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
    image = Image(url="https://example.com/image.jpg", public_id="test/image", is_thumbnail=True,
                  listing_id=hotel_id)
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
    response = await client.get("/listings?page=1&size=1")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["size"] == 1
    assert len(data["items"]) == 1

    # Act again for the second page
    response_page_2 = await client.get("/listings?page=2&size=1")

    # Assert for the second page
    assert response_page_2.status_code == 200
    data_page_2 = response_page_2.json()
    assert data_page_2["total"] == 2
    assert len(data_page_2["items"]) == 1
    # Ensure the items on page 1 and page 2 are different
    assert data["items"][0]["id"] != data_page_2["items"][0]["id"]
