import datetime
import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.guesthouse.schemas import GuesthouseBookingCreate
from src.bookings.models import Availability, GuesthouseBooking


async def get_availability_for_date_range(
        db: AsyncSession, listing_id: uuid.UUID, start_date: datetime.date, end_date: datetime.date
) -> Sequence[Availability]:
    """Retrieves availability records for a listing within a specific date range."""
    query = (
        select(Availability)
        .where(
            Availability.listing_id == listing_id,
            Availability.date >= start_date,
            Availability.date < end_date  # Exclude the check-out date
        )
    )
    result = await db.execute(query)
    return result.scalars().all()


async def create(
        db: AsyncSession, booking_in: GuesthouseBookingCreate, user_id: uuid.UUID, total_price: float
) -> GuesthouseBooking:
    """Creates a new guesthouse booking record."""
    db_booking = GuesthouseBooking(
        listing_id=booking_in.listing_id,
        check_in_date=booking_in.check_in_date,
        check_out_date=booking_in.check_out_date,
        number_of_rooms_booked=booking_in.number_of_rooms,
        user_id=user_id,
        total_price=total_price
    )
    db.add(db_booking)
    await db.flush()
    return db_booking
