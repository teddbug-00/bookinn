import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.cloudinary.client import CloudinaryClient
from src.cloudinary.dependencies import get_cloudinary_client
from src.database import get_db_session
from src.images import services as image_service
from src.images.schemas import ImageRead
from src.listings import services as listing_service
from src.listings.exceptions import NotListingOwnerException
from src.users.models import User

router = APIRouter(tags=["Images"])


@router.post("/listings/{listing_id}/images", status_code=status.HTTP_201_CREATED, response_model=ImageRead)
async def upload_image_for_listing(
        listing_id: uuid.UUID,
        file: UploadFile,
        is_thumbnail: Annotated[bool, Form()] = False,
        current_user: Annotated[User, Depends(get_current_user)] = None,
        session: AsyncSession = Depends(get_db_session),
        cloudinary_client: CloudinaryClient = Depends(get_cloudinary_client),
):
    """Uploads an image for a specific listing. Only the listing owner can perform this action."""
    listing = await listing_service.get_listing_by_id(session, listing_id)
    if listing.owner_id != current_user.id:
        raise NotListingOwnerException()

    image = await image_service.upload_listing_image(session, listing, file, is_thumbnail, cloudinary_client)
    return image
