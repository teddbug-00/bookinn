import datetime
import uuid
from typing import Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.models import Booking
from src.bookings.schemas import ApartmentBookingCreate


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


async def create(db: AsyncSession, booking_in: ApartmentBookingCreate, user_id: uuid.UUID, total_price: float,
                 check_out_date: datetime.date) -> Booking:
    """Creates a new booking record."""
    db_booking = Booking(
        **booking_in.model_dump(exclude={"type"}), user_id=user_id, total_price=total_price,
        check_out_date=check_out_date, type="apartment"
    )
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking


async def get_for_user(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Booking]:
    """Retrieves all bookings made by a specific user."""
    query = select(Booking).where(Booking.user_id == user_id).order_by(Booking.check_in_date.desc())
    result = await db.execute(query)
    return result.scalars().all()
