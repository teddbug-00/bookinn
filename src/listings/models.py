import uuid
from typing import List, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.amenities.models import Amenity, listing_amenities_association_table
from src.database import Base
from src.listings.enums import PricingUnit, ListingType

if TYPE_CHECKING:
    from src.users.models import User  # noqa
    from src.images.models import Image  # noqa
    from src.reviews.models import Review  # noqa


class Listing(Base):
    """Base model for all property listings."""
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)

    # Structured Location
    address: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)
    city: Mapped[str] = mapped_column(sa.String(length=100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(sa.Float, nullable=False)
    longitude: Mapped[float] = mapped_column(sa.Float, nullable=False)

    # Pricing and Policies
    price: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    price_unit: Mapped[PricingUnit] = mapped_column(sa.Enum(PricingUnit), nullable=False)
    currency: Mapped[str] = mapped_column(sa.String(3), nullable=False, default='GHS')
    # check_in_time: Mapped[Optional[time]] = mapped_column(sa.Time)
    # check_out_time: Mapped[Optional[time]] = mapped_column(sa.Time)
    # cancellation_policy: Mapped[Optional[str]] = mapped_column(sa.Text)
    # house_rules: Mapped[Optional[str]] = mapped_column(sa.Text)

    average_rating: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    amenities: Mapped[List[Amenity]] = relationship(secondary=listing_amenities_association_table,
                                                    back_populates="listings")

    owner_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"), index=True)
    owner: Mapped["User"] = relationship(back_populates="listings")

    images: Mapped[List["Image"]] = relationship(back_populates="listing", cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship(back_populates="listing", cascade="all, delete-orphan")

    # --- Inheritance Configuration ---
    type: Mapped[ListingType] = mapped_column(sa.Enum(ListingType))
    __mapper_args__ = {
        "polymorphic_identity": "listing",
        "polymorphic_on": "type",
    }

    @hybrid_property
    def amenity_ids(self) -> list[uuid.UUID]:
        """Provides a list of amenity IDs associated with the listing."""
        return [amenity.id for amenity in self.amenities]


class Hotel(Listing):
    """A hotel listing with specific attributes like star rating."""
    __tablename__ = "hotels"
    id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), primary_key=True)
    star_rating: Mapped[int] = mapped_column(sa.Integer, sa.CheckConstraint('star_rating >= 1 AND star_rating <= 5'),
                                             nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": ListingType.HOTEL,
    }


class Hostel(Listing):
    """A hostel listing with specific attributes for shared accommodations."""
    __tablename__ = "hostels"
    id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), primary_key=True)
    dorm_bed_count: Mapped[int | None] = mapped_column(sa.Integer)
    private_room_count: Mapped[int | None] = mapped_column(sa.Integer)

    __mapper_args__ = {
        "polymorphic_identity": ListingType.HOSTEL,
    }


class Apartment(Listing):
    """An apartment listing with details about rooms and facilities."""
    __tablename__ = "apartments"
    id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), primary_key=True)
    number_of_bedrooms: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    number_of_bathrooms: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    max_guests: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": ListingType.APARTMENT,
    }


class Guesthouse(Listing):
    """A guesthouse or B&B listing with a more personal touch."""
    __tablename__ = "guesthouses"
    id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("listings.id"), primary_key=True)
    number_of_rooms: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    host_on_site: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    __mapper_args__ = {
        "polymorphic_identity": ListingType.GUESTHOUSE,
    }
