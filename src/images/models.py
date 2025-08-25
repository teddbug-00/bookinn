import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.listings.models import Listing  # noqa


class Image(Base):
    """Represents an image associated with a listing."""
    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(sa.String(length=2048), nullable=False)
    listing_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), nullable=False, index=True)

    listing: Mapped["Listing"] = relationship(back_populates="images")
