from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.bookings.apartments import services as apartment_booking_service
from src.bookings.exceptions import InvalidListingTypeException
from src.bookings.schemas import BookingRead, ApartmentBookingCreate
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
    return await apartment_booking_service.get_user_bookings(session, current_user)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookingRead)
async def create_new_booking(
        booking_in: ApartmentBookingCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(get_db_session),
):
    """Creates a new booking for a listing."""
    listing = await listing_service.get_listing_by_id(session, booking_in.listing_id)

    if booking_in.type == ListingType.APARTMENT:
        booking = await apartment_booking_service.create_apartment_booking(session, booking_in, listing, current_user)
        return booking

    raise InvalidListingTypeException()
