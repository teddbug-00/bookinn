import datetime
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.bookings.enums import BookingStatus, BookingType
from src.database import Base

if TYPE_CHECKING:
    from src.listings.models import Listing, Guesthouse, Apartment  # noqa
    from src.users.models import User  # noqa


class Booking(Base):
    """Base model for all bookings."""
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_in_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    check_out_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    total_price: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(sa.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=sa.func.now())

    listing_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)

    listing: Mapped["Listing"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship(back_populates="bookings")

    # --- Inheritance Configuration ---
    __mapper_args__ = {
        "polymorphic_identity": "booking",
        "polymorphic_on": "type",
    }


class ApartmentBooking(Booking):
    """A booking specific to an apartment."""
    __tablename__ = "apartment_bookings"
    id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("bookings.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": BookingType.APARTMENT,
    }


class GuesthouseBooking(Booking):
    """A booking specific to a guesthouse, tracking the number of rooms."""
    __tablename__ = "guesthouse_bookings"
    id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("bookings.id"), primary_key=True)
    number_of_rooms_booked: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": BookingType.GUESTHOUSE,
    }


class Availability(Base):
    """Tracks the number of available units (e.g., rooms) for a listing on a specific date."""
    __tablename__ = "availability"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    available_units: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    listing_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), nullable=False, index=True)

    __table_args__ = (sa.UniqueConstraint('date', 'listing_id', name='_date_listing_uc'),)
