import uuid
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.listings.models import Listing
from src.reviews import repository as review_repository
from src.reviews.exceptions import CannotReviewOwnListingException, UserAlreadyReviewedListingException
from src.reviews.models import Review
from src.reviews.schemas import ReviewCreate
from src.users.models import User


async def get_reviews_for_listing(db: AsyncSession, listing_id: uuid.UUID) -> Sequence[Review]:
    """Retrieves all reviews for a specific listing."""
    return await review_repository.get_all_for_listing(db, listing_id)


async def create_review(db: AsyncSession, review_in: ReviewCreate, listing: Listing, reviewer: User) -> Review:
    """Creates a new review and updates the listing's average rating."""
    # Users cannot review their own listing.
    if listing.owner_id == reviewer.id:
        raise CannotReviewOwnListingException()

    # Users can only review a listing once.
    if await review_repository.get_by_listing_and_reviewer(db, listing.id, reviewer.id):
        raise UserAlreadyReviewedListingException(listing_id=listing.id, reviewer_id=reviewer.id)

    # Create the review
    db_review = await review_repository.create(db, review_in, listing.id, reviewer.id)

    # Update the listing's average rating
    avg_rating_query = select(func.avg(Review.rating)).where(Review.listing_id == listing.id)
    avg_rating_result = await db.execute(avg_rating_query)
    listing.average_rating = avg_rating_result.scalar()
    listing.total_reviews += 1

    db.add(listing)
    await db.commit()
    await db.refresh(db_review, attribute_names=["reviewer"])

    return db_review
