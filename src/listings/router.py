import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db_session
from src.listings import services as listing_service
from src.listings.schemas import ListingCreate, ListingRead, ListingSummaryRead, ListingUpdate
from src.pagination import Page, PaginationParams
from src.users.models import User

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get("/", response_model=Page[ListingSummaryRead], summary="Get all listings")
async def get_all_listings(
        pagination: PaginationParams = Depends(),
        session: AsyncSession = Depends(get_db_session)
):
    """ Retrieves a list of all available listings """
    return await listing_service.get_listings(session, pagination)


@router.get("/{listing_id}", response_model=ListingRead, summary="Get a single listing by ID")
async def get_single_listing(listing_id: uuid.UUID, session: AsyncSession = Depends(get_db_session)
                             ):
    """ Retrieves all info related to a listing by its ID """
    return await listing_service.get_listing_by_id(session, listing_id)


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
    listing = await listing_service.create_listing(db=session, listing_in=listing_in, owner_id=current_user.id)
    return listing


@router.patch("/{listing_id}", response_model=ListingRead, summary="Update a listing")
async def update_existing_listing(
        listing_id: uuid.UUID,
        listing_in: ListingUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """
    Updates a listing's details. Only the owner of the listing can perform this action.
    """
    return await listing_service.update_listing(session, listing_id, listing_in, current_user)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a listing")
async def delete_existing_listing(
        listing_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """
    Deletes a listing. Only the owner of the listing can perform this action.
    """
    await listing_service.delete_listing(session, listing_id, current_user)
    return None
