import pytest
from httpx import AsyncClient


@pytest.fixture
async def listing_owner_client(client_factory) -> AsyncClient:
    """Provides an authenticated client who will own the listings."""
    owner_client = client_factory()
    user_data = {
        "email": "owner@example.com",
        "password": "ownerpassword",
        "name": "Listing Owner",
        "date_of_birth": "1990-01-01"
    }
    await owner_client.post("/users/", json=user_data)
    login_response = await owner_client.post("/auth/login",
                                             json={"email": user_data["email"], "password": user_data["password"]})
    token = login_response.json()["access_token"]
    owner_client.headers["Authorization"] = f"Bearer {token}"
    return owner_client


@pytest.fixture
async def reviewer_client(client_factory) -> AsyncClient:
    """Provides a separate authenticated client to act as the reviewer."""
    reviewer_client = client_factory()
    user_data = {
        "email": "reviewer@example.com",
        "password": "reviewerpassword",
        "name": "Reviewer User",
        "date_of_birth": "1992-02-02"
    }
    # We use the new client to register and log in the reviewer
    await reviewer_client.post("/users/", json=user_data)
    login_response = await reviewer_client.post("/auth/login",
                                                json={"email": user_data["email"], "password": user_data["password"]})
    token = login_response.json()["access_token"]
    reviewer_client.headers["Authorization"] = f"Bearer {token}"
    return reviewer_client


@pytest.mark.asyncio
async def test_create_and_get_reviews(listing_owner_client: AsyncClient, reviewer_client: AsyncClient):
    """Test creating a review and then fetching it."""
    # 1. Create a listing as the owner
    listing_data = {"type": "hotel", "name": "Test Hotel", "address": "123 Test St", "city": "Testville",
                    "latitude": 1.0, "longitude": 1.0, "price": 100.0, "price_unit": "per_night", "star_rating": 4}
    create_res = await listing_owner_client.post("/listings/", json=listing_data)
    assert create_res.status_code == 201
    listing_id = create_res.json()["id"]

    # 2. Create a review as the reviewer
    review_data = {"rating": 5, "comment": "Excellent stay!"}
    review_res = await reviewer_client.post(f"/listings/{listing_id}/reviews", json=review_data)
    assert review_res.status_code == 201
    review_json = review_res.json()
    assert review_json["rating"] == 5
    assert review_json["comment"] == "Excellent stay!"
    assert "reviewer" in review_json
    assert review_json["reviewer"]["name"] == "Reviewer User"

    # 3. Verify the listing's average rating was updated
    listing_res = await listing_owner_client.get(f"/listings/{listing_id}")
    assert listing_res.status_code == 200
    assert listing_res.json()["average_rating"] == 5.0

    # 4. Get all reviews for the listing
    get_reviews_res = await listing_owner_client.get(f"/listings/{listing_id}/reviews")
    assert get_reviews_res.status_code == 200
    reviews_list = get_reviews_res.json()
    assert len(reviews_list) == 1
    assert reviews_list[0]["comment"] == "Excellent stay!"


@pytest.mark.asyncio
async def test_create_review_on_own_listing(listing_owner_client: AsyncClient):
    """Test that a user cannot review their own listing."""
    listing_data = {"type": "hotel", "name": "Self-Review Hotel", "address": "123 Self St", "city": "Selftown",
                    "latitude": 1.0, "longitude": 1.0, "price": 100.0, "price_unit": "per_night", "star_rating": 4}
    create_res = await listing_owner_client.post("/listings/", json=listing_data)
    listing_id = create_res.json()["id"]

    review_data = {"rating": 1, "comment": "This should fail."}
    review_res = await listing_owner_client.post(f"/listings/{listing_id}/reviews", json=review_data)
    assert review_res.status_code == 403
    assert "cannot review your own listing" in review_res.json()["detail"]


@pytest.mark.asyncio
async def test_create_duplicate_review(listing_owner_client: AsyncClient, reviewer_client: AsyncClient):
    """Test that a user cannot review the same listing twice."""
    listing_data = {"type": "hotel", "name": "Duplicate Review Hotel", "address": "123 Dupe St", "city": "Dupetown",
                    "latitude": 1.0, "longitude": 1.0, "price": 100.0, "price_unit": "per_night", "star_rating": 4}
    create_res = await listing_owner_client.post("/listings/", json=listing_data)
    listing_id = create_res.json()["id"]

    review_data = {"rating": 4, "comment": "First review."}
    await reviewer_client.post(f"/listings/{listing_id}/reviews", json=review_data)

    # Attempt to post a second review
    second_review_res = await reviewer_client.post(f"/listings/{listing_id}/reviews", json={"rating": 2})
    assert second_review_res.status_code == 409
    assert "has already reviewed listing" in second_review_res.json()["detail"]
