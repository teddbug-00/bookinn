import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_polymorphic

from src.listings.models import Listing, Hotel, Apartment, Hostel, Guesthouse


async def get_all(db: AsyncSession) -> Sequence[Listing]:
    """Retrieves all listings, eagerly loading their amenities."""
    # Use with_polymorphic to eagerly load all subclass-specific columns
    polymorphic_listing = with_polymorphic(Listing, [Hotel, Apartment, Hostel, Guesthouse])
    query = (select(polymorphic_listing)
             .options(selectinload(polymorphic_listing.amenities), selectinload(polymorphic_listing.images))
             .order_by(polymorphic_listing.name)
             )
    result = await db.execute(query)
    return result.scalars().all()


async def get_by_id(db: AsyncSession, listing_id: uuid.UUID) -> Optional[Listing]:
    """Retrieves a single listing by its ID, eagerly loading its amenities."""
    # Use with_polymorphic to eagerly load all subclass-specific columns
    polymorphic_listing = with_polymorphic(Listing, [Hotel, Apartment, Hostel, Guesthouse])
    query = (select(polymorphic_listing)
             .options(selectinload(polymorphic_listing.amenities), selectinload(polymorphic_listing.images))
             .where(listing_id == polymorphic_listing.id))
    result = await db.execute(query)
    return result.scalar_one_or_none()
