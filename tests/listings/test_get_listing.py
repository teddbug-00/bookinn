import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.images.models import Image


@pytest.mark.asyncio
async def test_get_single_listing_by_id(client: AsyncClient, authenticated_client: AsyncClient,
                                        test_session: AsyncSession):
    """Test retrieving a single, specific listing by its ID."""
    listing_data = {
        "type": "guesthouse", "name": "Gamma Guesthouse", "address": "789 Gamma Rd", "city": "Gammaton",
        "latitude": 3.0, "longitude": 3.0, "price": 80.0, "price_unit": "per_night", "number_of_rooms": 5
    }
    create_response = await authenticated_client.post("/listings/", json=listing_data)
    listing_id = uuid.UUID(create_response.json()["id"])  # Convert string to UUID object

    # Create an image associated with the listing
    image = Image(url="https://example.com/gamma.jpg", is_thumbnail=True, listing_id=listing_id)
    test_session.add(image)
    await test_session.commit()

    response = await client.get(f"/listings/{listing_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Gamma Guesthouse"
    assert len(data["images"]) == 1
    assert data["images"][0]["url"] == "https://example.com/gamma.jpg"
    assert data["images"][0]["is_thumbnail"] is True


@pytest.mark.asyncio
async def test_get_single_listing_not_found(client: AsyncClient):
    """Test that requesting a non-existent listing ID returns a 404 error."""
    non_existent_id = uuid.uuid4()
    response = await client.get(f"/listings/{non_existent_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
