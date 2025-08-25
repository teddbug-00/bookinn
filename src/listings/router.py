from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db_session
from src.listings import services
from src.listings.schemas import ListingCreate, ListingRead
from src.users.models import User

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ListingRead)
async def create_new_listing(
        listing_in: ListingCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """
    Creates a new listing.
    The request body must contain a `type` field (`hotel` or `apartment`) which determines the other required fields.
    """
    listing = await services.create_listing(db=session, listing_in=listing_in, owner_id=current_user.id)
    return listing
