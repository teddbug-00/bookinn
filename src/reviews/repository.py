import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.reviews.models import Review
from src.reviews.schemas import ReviewCreate


async def get_all_for_listing(db: AsyncSession, listing_id: uuid.UUID) -> Sequence[Review]:
    """Retrieves all reviews for a specific listing, ordered by creation date."""
    query = (select(Review)
             .where(Review.listing_id == listing_id)
             .options(selectinload(Review.reviewer))
             .order_by(Review.created_at.desc()))
    result = await db.execute(query)
    return result.scalars().all()


async def get_by_listing_and_reviewer(db: AsyncSession, listing_id: uuid.UUID, reviewer_id: uuid.UUID) -> Optional[
    Review]:
    """Checks if a specific user has already reviewed a specific listing."""
    query = select(Review).where(Review.listing_id == listing_id, Review.reviewer_id == reviewer_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, review_in: ReviewCreate, listing_id: uuid.UUID, reviewer_id: uuid.UUID) -> Review:
    """Creates a new review object and adds it to the session."""
    db_review = Review(**review_in.model_dump(), listing_id=listing_id, reviewer_id=reviewer_id)
    db.add(db_review)
    await db.flush()
    return db_review
