import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.amenities.models import Amenity
from src.listings import models
from src.listings.exceptions import InvalidAmenitiesException
from src.listings.schemas import ListingCreate


async def get_amenities_by_ids(db: AsyncSession, amenity_ids: List[uuid.UUID]) -> List[Amenity]:
    """Fetches a list of Amenity objects from a list of IDs, raising an error if any are not found."""
    if not amenity_ids:
        return []

    query = select(Amenity).where(Amenity.id.in_(amenity_ids))
    result = await db.execute(query)
    amenities = result.scalars().all()

    if len(amenities) != len(set(amenity_ids)):
        found_ids = {amenity.id for amenity in amenities}
        invalid_ids = [str(aid) for aid in amenity_ids if aid not in found_ids]
        raise InvalidAmenitiesException(invalid_ids=invalid_ids)

    return amenities


async def create_listing(db: AsyncSession, listing_in: ListingCreate, owner_id: uuid.UUID) -> models.Listing:
    """Creates a new listing, validating and associating amenities."""
    model_class = getattr(models, listing_in.type.value.capitalize())

    amenities = await get_amenities_by_ids(db, listing_in.amenity_ids)

    listing_data = listing_in.model_dump(exclude={"amenity_ids"})
    db_listing = model_class(**listing_data, owner_id=owner_id)
    db_listing.amenities = amenities

    db.add(db_listing)
    await db.commit()
    await db.refresh(db_listing, attribute_names=["amenities", "owner"])

    return db_listing
