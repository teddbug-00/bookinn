import datetime
import uuid
from typing import Sequence, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.models import Booking


async def check_for_overlapping_bookings(
        db: AsyncSession, listing_id: uuid.UUID, check_in: datetime.date, check_out: datetime.date
) -> bool:
    """Checks if any confirmed bookings overlap with the given date range."""
    query = select(Booking).where(
        Booking.listing_id == listing_id,
        or_(
            and_(Booking.check_in_date < check_out, Booking.check_out_date > check_in),
        )
    )
    result = await db.execute(select(query.exists()))
    return result.scalar()


async def get_for_user(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Booking]:
    """Retrieves all bookings made by a specific user."""
    query = select(Booking).where(Booking.user_id == user_id).order_by(Booking.check_in_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_by_id(db: AsyncSession, booking_id: uuid.UUID) -> Optional[Booking]:
    """Retrieves a single booking by its ID."""
    return await db.get(Booking, booking_id)


async def delete(db: AsyncSession, db_booking: Booking) -> None:
    """Deletes a booking record from the database."""
    await db.delete(db_booking)
