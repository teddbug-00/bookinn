import uuid
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_polymorphic

from src.listings.models import Listing, Hotel, Apartment, Hostel, Guesthouse


async def get_all(db: AsyncSession, offset: int, limit: int) -> (Sequence[Listing], int):
    """Retrieves a paginated list of listings and the total count."""
    # Use with_polymorphic to eagerly load all subclass-specific columns
    polymorphic_listing = with_polymorphic(Listing, [Hotel, Apartment, Hostel, Guesthouse])

    # Query for the paginated items
    query = (select(polymorphic_listing)
             .options(selectinload(polymorphic_listing.amenities), selectinload(polymorphic_listing.images))
             .order_by(polymorphic_listing.name)
             .offset(offset)
             .limit(limit)
             )
    result = await db.execute(query)
    items = result.scalars().all()

    # Query for the total count
    count_query = select(func.count(Listing.id))
    total = (await db.execute(count_query)).scalar_one()

    return items, total


async def get_by_id(db: AsyncSession, listing_id: uuid.UUID) -> Optional[Listing]:
    """Retrieves a single listing by its ID, eagerly loading its amenities."""
    # Use with_polymorphic to eagerly load all subclass-specific columns
    polymorphic_listing = with_polymorphic(Listing, [Hotel, Apartment, Hostel, Guesthouse])
    query = (select(polymorphic_listing)
             .options(selectinload(polymorphic_listing.amenities), selectinload(polymorphic_listing.images))
             .where(listing_id == polymorphic_listing.id))
    result = await db.execute(query)
    return result.scalar_one_or_none()
