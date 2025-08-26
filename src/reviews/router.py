import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db_session
from src.listings import services as listing_service
from src.reviews import services as review_service
from src.reviews.schemas import ReviewCreate, ReviewRead
from src.users.models import User

router = APIRouter(tags=["Reviews"])


@router.get("/listings/{listing_id}/reviews", response_model=Sequence[ReviewRead])
async def get_listing_reviews(
        listing_id: uuid.UUID,
        session: AsyncSession = Depends(get_db_session)
):
    """Get all reviews for a specific listing."""
    # This also implicitly validates that the listing exists
    await listing_service.get_listing_by_id(session, listing_id)
    return await review_service.get_reviews_for_listing(session, listing_id)


@router.post("/listings/{listing_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=ReviewRead)
async def create_listing_review(
        listing_id: uuid.UUID,
        review_in: ReviewCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """Create a new review for a specific listing."""
    listing = await listing_service.get_listing_by_id(session, listing_id)
    review = await review_service.create_review(session, review_in, listing, current_user)
    return review
