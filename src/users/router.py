from typing import Annotated

from fastapi import APIRouter, Depends, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.cloudinary.client import CloudinaryClient
from src.cloudinary.dependencies import get_cloudinary_client
from src.database import get_db_session
from src.users import services
from src.users.models import User
from src.users.schemas import UserCreate, UserRead, UserUpdate  # Import UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserRead, summary="Get current user profile")
async def read_current_user_profile(
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retrieves the details for the currently authenticated user.
    """
    return current_user


@router.patch("/profile", response_model=UserRead, summary="Update current user profile")
async def update_current_user_profile(
        user_in: UserUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """
    Updates the profile for the currently authenticated user.
    """
    user = await services.update_user(db=session, user=current_user, user_in=user_in)
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead, summary="Register a new user")
async def register_user(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_db_session),
):
    """Registers a new user (creates a user resource)."""
    user = await services.create_user(db=session, user_in=user_in)
    return user


@router.post("/profile/picture", response_model=UserRead, summary="Upload a profile picture")
async def upload_profile_picture(
        file: UploadFile,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
        cloudinary_client: CloudinaryClient = Depends(get_cloudinary_client),
):
    """
    Uploads or replaces the profile picture for the currently authenticated user.
    """
    user = await services.set_profile_picture(
        db=session, user=current_user, file=file, client=cloudinary_client
    )
    return user
