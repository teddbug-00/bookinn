from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db_session
from src.users import services
from src.users.models import User
from src.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserRead, summary="Get current user profile")
async def read_current_user_profile(
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retrieves the details for the currently authenticated user.
    """
    return current_user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead, summary="Register a new user")
async def register_user(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_db_session),
):
    """Registers a new user (creates a user resource)."""
    user = await services.create_user(db=session, user_in=user_in)
    return user
