import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.images.models import Image
from src.images.schemas import ImageCreate


async def get_thumbnail_for_listing(db: AsyncSession, listing_id: uuid.UUID) -> Optional[Image]:
    """Retrieves the thumbnail image for a given listing, if it exists."""
    query = select(Image).where(Image.listing_id == listing_id, Image.is_thumbnail == True)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, image_id: uuid.UUID) -> Optional[Image]:
    """Retrieves a single image by its ID."""
    return await db.get(Image, image_id)


async def get_by_id_with_listing(db: AsyncSession, image_id: uuid.UUID) -> Optional[Image]:
    """Retrieves a single image by its ID, eagerly loading the parent listing."""
    query = select(Image).options(selectinload(Image.listing)).where(Image.id == image_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, image_in: ImageCreate, public_id: str) -> Image:
    """Creates a new image record in the database."""
    db_image = Image(**image_in.model_dump(), public_id=public_id)
    db.add(db_image)
    await db.flush()
    return db_image


async def delete(db: AsyncSession, db_image: Image) -> None:
    """Deletes an image record from the database."""
    await db.delete(db_image)
    await db.flush()
