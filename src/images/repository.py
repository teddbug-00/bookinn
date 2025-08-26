import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.images.models import Image
from src.images.schemas import ImageCreate


async def get_thumbnail_for_listing(db: AsyncSession, listing_id: uuid.UUID) -> Optional[Image]:
    """Retrieves the thumbnail image for a given listing, if it exists."""
    query = select(Image).where(Image.listing_id == listing_id, Image.is_thumbnail == True)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, image_in: ImageCreate) -> Image:
    """Creates a new image record in the database."""
    db_image = Image(**image_in.model_dump())
    db.add(db_image)
    await db.flush()
    return db_image
