import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings import repository as booking_repository
from src.bookings.exceptions import NotBookingOwnerException
from src.bookings.models import Booking
from src.users.models import User


async def get_user_bookings(db: AsyncSession, user: User) -> Sequence[Booking]:
    """Retrieves all bookings for the currently authenticated user."""
    return await booking_repository.get_for_user(db, user.id)


async def cancel_booking(db: AsyncSession, booking_id: uuid.UUID, user: User) -> None:
    """Cancels a booking, ensuring the user is the owner."""
    db_booking = await booking_repository.get_by_id(db, booking_id)

    if not db_booking or db_booking.user_id != user.id:
        raise NotBookingOwnerException()

    await booking_repository.delete(db, db_booking)
    await db.commit()
    return None
