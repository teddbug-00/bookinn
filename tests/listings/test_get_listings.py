import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_listings_empty(client: AsyncClient):
    """Test retrieving all listings when none have been created."""
    response = await client.get("/listings/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_listings_with_data(client: AsyncClient, authenticated_client: AsyncClient):
    """Test retrieving all listings when multiple exist."""
    # Create a hotel
    hotel_data = {
        "type": "hotel", "name": "Alpha Hotel", "address": "123 Alpha St", "city": "Alphaville",
        "latitude": 1.0, "longitude": 1.0, "price": 100.0, "price_unit": "per_night", "star_rating": 4
    }
    await authenticated_client.post("/listings/", json=hotel_data)

    # Create an apartment
    apartment_data = {
        "type": "apartment", "name": "Beta Apartments", "address": "456 Beta Ave", "city": "Betatown",
        "latitude": 2.0, "longitude": 2.0, "price": 1500.0, "price_unit": "per_month",
        "number_of_bedrooms": 2, "number_of_bathrooms": 1, "max_guests": 4
    }
    await authenticated_client.post("/listings/", json=apartment_data)

    # Act
    response = await client.get("/listings/")

    # Assert
    assert response.status_code == 200
    listings = response.json()
    assert len(listings) == 2
    assert {listing['name'] for listing in listings} == {"Alpha Hotel", "Beta Apartments"}
