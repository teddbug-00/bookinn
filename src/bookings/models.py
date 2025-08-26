import datetime
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.bookings.enums import BookingStatus
from src.database import Base

if TYPE_CHECKING:
    from src.listings.models import Listing  # noqa
    from src.users.models import User  # noqa


class Booking(Base):
    """Represents a booking made by a user for a listing."""
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_in_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    check_out_date: Mapped[datetime.date] = mapped_column(sa.Date, nullable=False)
    total_price: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(sa.Enum(BookingStatus), default=BookingStatus.PENDING)
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=sa.func.now())

    listing_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)

    listing: Mapped["Listing"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship(back_populates="bookings")
