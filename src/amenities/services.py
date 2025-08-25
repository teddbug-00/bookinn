import uuid
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.amenities.exceptions import AmenityAlreadyExistsException, AmenityNotFoundException
from src.amenities.models import Amenity
from src.amenities.schemas import AmenityCreate, AmenityUpdate


async def get_amenity_by_name(db: AsyncSession, name: str) -> Optional[Amenity]:
    """Retrieves an amenity by its name."""
    query = select(Amenity).where(Amenity.name == name)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_amenity(db: AsyncSession, amenity_in: AmenityCreate) -> Amenity:
    """Creates a new amenity in the database."""
    if await get_amenity_by_name(db, amenity_in.name):
        raise AmenityAlreadyExistsException(name=amenity_in.name)
    db_amenity = Amenity(**amenity_in.model_dump())
    db.add(db_amenity)
    await db.commit()
    await db.refresh(db_amenity)
    return db_amenity


async def get_amenities(db: AsyncSession) -> Sequence[Amenity]:
    """Retrieves all amenities from the database."""
    query = select(Amenity).order_by(Amenity.name)
    result = await db.execute(query)
    return result.scalars().all()


async def get_amenity_by_id(db: AsyncSession, amenity_id: uuid.UUID) -> Amenity:
    """Retrieves a single amenity by its ID."""
    amenity = await db.get(Amenity, amenity_id)
    if not amenity:
        raise AmenityNotFoundException(amenity_id)
    return amenity


async def update_amenity(db: AsyncSession, amenity: Amenity, amenity_in: AmenityUpdate) -> Amenity:
    """Updates an amenity's information."""
    update_data = amenity_in.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing_amenity = await get_amenity_by_name(db, update_data["name"])
        if existing_amenity and existing_amenity.id != amenity.id:
            raise AmenityAlreadyExistsException(name=update_data["name"])
    for field, value in update_data.items():
        setattr(amenity, field, value)
    await db.commit()
    await db.refresh(amenity)
    return amenity


async def delete_amenity(db: AsyncSession, amenity_id: uuid.UUID) -> None:
    """Deletes an amenity from the database."""
    amenity = await get_amenity_by_id(db, amenity_id)
    await db.delete(amenity)
    await db.commit()
    return None
