from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.cloudinary import upload_image
from src.images import repository as image_repository
from src.images.exceptions import ThumbnailAlreadyExistsException
from src.images.models import Image
from src.images.schemas import ImageCreate
from src.listings.models import Listing


async def upload_listing_image(
        db: AsyncSession, listing: Listing, file: UploadFile, is_thumbnail: bool
) -> Image:
    """
    Handles the business logic of uploading an image for a listing.
    """
    # If setting a new thumbnail, check if one already exists.
    if is_thumbnail:
        existing_thumbnail = await image_repository.get_thumbnail_for_listing(db, listing.id)
        if existing_thumbnail:
            raise ThumbnailAlreadyExistsException()

    # Upload the image to cloudinary in a "listings" folder
    upload_result = await upload_image(file, folder="listing")
    image_url = upload_result.get("secure_url")

    image_data = ImageCreate(url=image_url, is_thumbnail=is_thumbnail, listing_id=listing.id)
    db_image = await image_repository.create(db, image_data)

    await db.commit()
    await db.refresh(db_image)
    return db_image
