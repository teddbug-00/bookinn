from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.apartment.schemas import ApartmentBookingCreate
from src.bookings.models import ApartmentBooking


async def create(db: AsyncSession, booking_in: ApartmentBookingCreate, user_id, total_price,
                 check_out_date) -> ApartmentBooking:
    """Creates a new apartment booking record."""
    db_booking = ApartmentBooking(
        listing_id=booking_in.listing_id,
        check_in_date=booking_in.check_in_date,
        check_out_date=check_out_date,
        user_id=user_id,
        total_price=total_price
    )
    db.add(db_booking)
    await db.flush()
    return db_booking