import uuid
from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.listings.models import Listing  # noqa

# Association table for the many-to-many relationship between listings and amenities
listing_amenities_association_table = sa.Table(
    "listing_amenities",
    Base.metadata,
    sa.Column("listing_id", sa.ForeignKey("listings.id"), primary_key=True),
    sa.Column("amenity_id", sa.ForeignKey("amenities.id"), primary_key=True),
)


class Amenity(Base):
    """Represents a distinct amenity that can be associated with listings."""
    __tablename__ = "amenities"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(length=100), unique=True, nullable=False)
    listings: Mapped[List["Listing"]] = relationship(secondary=listing_amenities_association_table,
                                                     back_populates="amenities")
