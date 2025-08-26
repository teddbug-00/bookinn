import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.amenities.models import Amenity
from src.amenities.schemas import AmenityCreate


async def get_by_name(db: AsyncSession, name: str) -> Optional[Amenity]:
    """Retrieves an amenity by its name."""
    query = select(Amenity).where(Amenity.name == name)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, amenity_id: uuid.UUID) -> Optional[Amenity]:
    """Retrieves a single amenity by its ID."""
    return await db.get(Amenity, amenity_id)


async def get_all(db: AsyncSession) -> Sequence[Amenity]:
    """Retrieves all amenities from the database."""
    query = select(Amenity).order_by(Amenity.name)
    result = await db.execute(query)
    return result.scalars().all()


async def get_by_ids(db: AsyncSession, amenity_ids: list[uuid.UUID]) -> Sequence[Amenity]:
    """Retrieves a list of amenities by their IDs."""
    if not amenity_ids:
        return []
    query = select(Amenity).where(Amenity.id.in_(amenity_ids))
    result = await db.execute(query)
    return result.scalars().all()


async def create(db: AsyncSession, amenity_in: AmenityCreate) -> Amenity:
    """Creates a new amenity object and adds it to the session."""
    db_amenity = Amenity(**amenity_in.model_dump())
    db.add(db_amenity)
    await db.flush()
    return db_amenity


async def delete(db: AsyncSession, db_amenity: Amenity) -> None:
    """Deletes an amenity object from the session."""
    await db.delete(db_amenity)
    await db.flush()
    return None
