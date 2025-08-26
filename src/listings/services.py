import uuid
from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.amenities import repository as amenity_repository
from src.listings import models, repository as listing_repository
from src.listings.exceptions import InvalidAmenitiesException, ListingNotFoundException, NotListingOwnerException
from src.listings.schemas import ListingCreate, ListingUpdate
from src.users.models import User


async def _validate_and_get_amenities(db: AsyncSession, amenity_ids: List[uuid.UUID]) -> List[models.Amenity]:
    """Helper to fetch and validate amenities for a new listing."""
    if not amenity_ids:
        return []

    amenities = await amenity_repository.get_by_ids(db, amenity_ids)

    if len(amenities) != len(set(amenity_ids)):
        found_ids = {amenity.id for amenity in amenities}
        invalid_ids = [str(amenity_id) for amenity_id in amenity_ids if amenity_id not in found_ids]
        raise InvalidAmenitiesException(invalid_ids=invalid_ids)

    return list(amenities)


async def create_listing(db: AsyncSession, listing_in: ListingCreate, owner_id: uuid.UUID) -> models.Listing:
    """Creates a new listing, validating and associating amenities."""
    model_class = getattr(models, listing_in.type.value.capitalize())

    amenities = await _validate_and_get_amenities(db, listing_in.amenity_ids)

    listing_data = listing_in.model_dump(exclude={"amenity_ids"})
    db_listing = model_class(**listing_data, owner_id=owner_id)
    db_listing.amenities = amenities

    db.add(db_listing)
    await db.commit()

    # After commit, the object is expired. To get the relationships loaded
    # for the response model, we need to re-fetch it from the database
    # with the extra relationships.
    query = (
        select(models.Listing)
        .options(
            selectinload(models.Listing.amenities),
            selectinload(models.Listing.images)
        )
        .where(models.Listing.id == db_listing.id)
    )
    result = await db.execute(query)
    refreshed_listing = result.scalar_one()

    return refreshed_listing


async def get_listings(db: AsyncSession) -> Sequence[models.Listing]:
    """Retrieves all listings from the database."""
    return await listing_repository.get_all(db)


async def get_listing_by_id(db: AsyncSession, listing_id: uuid.UUID) -> models.Listing:
    """Retrieves a single listing by its ID, raising an error if not found."""
    db_listing = await listing_repository.get_by_id(db, listing_id)
    if not db_listing:
        raise ListingNotFoundException(listing_id)
    return db_listing


async def update_listing(
        db: AsyncSession, listing_id: uuid.UUID, listing_in: ListingUpdate, current_user: User
) -> models.Listing:
    """Updates a listing's details, ensuring the user is the owner."""
    db_listing = await get_listing_by_id(db, listing_id)

    # Business Rule: Only the owner can update their listing.
    if db_listing.owner_id != current_user.id:
        raise NotListingOwnerException()

    update_data = listing_in.model_dump(exclude_unset=True)

    if "amenity_ids" in update_data:
        db_listing.amenities = await _validate_and_get_amenities(db, update_data.pop("amenity_ids"))

    for field, value in update_data.items():
        setattr(db_listing, field, value)

    db.add(db_listing)
    await db.commit()

    # After commit, relationships might be expired. We need to re-fetch the
    # listing with all the relationships required by the response model.
    query = (
        select(models.Listing)
        .options(selectinload(models.Listing.amenities), selectinload(models.Listing.images))
        .where(models.Listing.id == db_listing.id)
    )
    result = await db.execute(query)
    return result.scalar_one()


async def delete_listing(db: AsyncSession, listing_id: uuid.UUID, current_user: User) -> None:
    """Deletes a listing, ensuring the user is the owner."""
    db_listing = await get_listing_by_id(db, listing_id)

    if db_listing.owner_id != current_user.id:
        raise NotListingOwnerException()

    await db.delete(db_listing)
    await db.commit()
    return None
