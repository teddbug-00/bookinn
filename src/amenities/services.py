import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.amenities import repository as amenity_repository
from src.amenities.exceptions import AmenityAlreadyExistsException, AmenityNotFoundException
from src.amenities.models import Amenity
from src.amenities.schemas import AmenityCreate, AmenityUpdate


async def create_amenity(db: AsyncSession, amenity_in: AmenityCreate) -> Amenity:
    """Creates a new amenity in the database."""
    # Business logic: check for duplicates
    if await amenity_repository.get_by_name(db, amenity_in.name):
        raise AmenityAlreadyExistsException(name=amenity_in.name)

    # Data access
    db_amenity = await amenity_repository.create(db, amenity_in)
    await db.commit()
    await db.refresh(db_amenity)
    return db_amenity


async def get_amenities(db: AsyncSession) -> Sequence[Amenity]:
    """Retrieves all amenities from the database."""
    return await amenity_repository.get_all(db)


async def get_amenity_by_id(db: AsyncSession, amenity_id: uuid.UUID) -> Amenity:
    """Retrieves a single amenity by its ID, raising an error if not found."""
    db_amenity = await amenity_repository.get_by_id(db, amenity_id)
    if not db_amenity:
        raise AmenityNotFoundException(amenity_id)
    return db_amenity


async def update_amenity(db: AsyncSession, amenity: Amenity, amenity_in: AmenityUpdate) -> Amenity:
    """Updates an amenity's information."""
    # Business logic: check for name conflicts on update
    update_data = amenity_in.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing_amenity = await amenity_repository.get_by_name(db, update_data["name"])
        if existing_amenity and existing_amenity.id != amenity.id:
            raise AmenityAlreadyExistsException(name=update_data["name"])

    # Data access
    for field, value in update_data.items():
        setattr(amenity, field, value)
    db.add(amenity)
    await db.commit()
    await db.refresh(amenity)
    return amenity


async def delete_amenity(db: AsyncSession, amenity_id: uuid.UUID) -> None:
    """Deletes an amenity from the database."""
    # Business logic: ensure amenity exists before trying to delete
    amenity_to_delete = await get_amenity_by_id(db, amenity_id)

    # Data access
    await amenity_repository.delete(db, amenity_to_delete)
    await db.commit()
    return None
