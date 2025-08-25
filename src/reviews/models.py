import datetime
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.listings.models import Listing  # noqa
    from src.users.models import User  # noqa


class Review(Base):
    """Represents a review left by a user for a listing."""
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rating: Mapped[int] = mapped_column(sa.Integer, sa.CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment: Mapped[str | None] = mapped_column(sa.Text)
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=sa.func.now())

    listing_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), nullable=False, index=True)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)

    listing: Mapped["Listing"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")
