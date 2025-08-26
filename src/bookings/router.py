import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.bookings import services as generic_booking_service
from src.bookings.apartment import services as apartment_service
from src.bookings.guesthouse import services as guesthouse_service
from src.bookings.schemas import BookingCreate, BookingRead
from src.database import get_db_session
from src.listings import services as listing_service
from src.listings.enums import ListingType
from src.users.models import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/my-bookings", response_model=Sequence[BookingRead])
async def get_my_bookings(
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """Retrieves all bookings made by the currently authenticated user."""
    return await generic_booking_service.get_user_bookings(session, current_user)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookingRead)
async def create_new_booking(
        booking_in: BookingCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """Creates a new booking for a listing."""
    listing = await listing_service.get_listing_by_id(session, booking_in.listing_id)

    if booking_in.type == ListingType.APARTMENT:
        return await apartment_service.create_apartment_booking(session, booking_in, listing, current_user)
    elif booking_in.type == ListingType.GUESTHOUSE:
        return await guesthouse_service.create_guesthouse_booking(session, booking_in, listing, current_user)
    return None


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_a_booking(
        booking_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """Cancels a booking. Only the user who made the booking can perform this action."""
    await generic_booking_service.cancel_booking(session, booking_id, current_user)
    return None
