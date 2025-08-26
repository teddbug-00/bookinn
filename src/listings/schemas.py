import uuid
from typing import Annotated, List, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from src.images.schemas import ImageRead
from src.listings.enums import ListingType, PricingUnit


class ListingSummaryRead(BaseModel):
    """A slimmed-down schema for representing a listing in a list view."""
    id: uuid.UUID
    name: str
    address: str
    average_rating: float | None = None
    total_reviews: int = 0
    thumbnail_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Shared Schemas ---
class AmenityInListingRead(BaseModel):
    id: uuid.UUID
    name: str
    icon_url: str | None

    model_config = ConfigDict(from_attributes=True)


# --- Base Schemas ---
class ListingBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    address: str
    city: str
    latitude: float
    longitude: float
    price: float = Field(..., gt=0)
    price_unit: PricingUnit
    currency: str = "GHS"
    amenity_ids: List[uuid.UUID] = []


# --- Create Schemas (for request body) ---
class HotelCreate(ListingBase):
    type: Literal[ListingType.HOTEL] = ListingType.HOTEL
    star_rating: int = Field(..., ge=1, le=5)


class ApartmentCreate(ListingBase):
    type: Literal[ListingType.APARTMENT] = ListingType.APARTMENT
    number_of_bedrooms: int = Field(..., gt=0)
    number_of_bathrooms: int = Field(..., gt=0)
    max_guests: int = Field(..., gt=0)


class HostelCreate(ListingBase):
    type: Literal[ListingType.HOSTEL] = ListingType.HOSTEL
    dorm_bed_count: int | None = None
    private_room_count: int | None = None


class GuesthouseCreate(ListingBase):
    type: Literal[ListingType.GUESTHOUSE] = ListingType.GUESTHOUSE
    number_of_rooms: int = Field(..., gt=0)
    host_on_site: bool = True


# A discriminated union for FastAPI to validate the request body against
ListingCreate = Annotated[
    Union[HotelCreate, ApartmentCreate, GuesthouseCreate, HostelCreate],
    Field(discriminator="type")
]


# --- Update Schemas (for PATCH request body) ---
class ListingUpdate(BaseModel):
    """Base schema for updating a listing, all fields are optional."""
    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    address: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    price: float | None = Field(None, gt=0)
    price_unit: PricingUnit | None = None
    amenity_ids: List[uuid.UUID] | None = None


class HotelUpdate(ListingUpdate):
    star_rating: int | None = Field(None, ge=1, le=5)


class ApartmentUpdate(ListingUpdate):
    number_of_bedrooms: int | None = Field(None, gt=0)
    number_of_bathrooms: int | None = Field(None, gt=0)
    max_guests: int | None = Field(None, gt=0)


class HostelUpdate(ListingUpdate):
    dorm_bed_count: int | None = None
    private_room_count: int | None = None


class GuesthouseUpdate(ListingUpdate):
    number_of_rooms: int | None = Field(None, gt=0)
    host_on_site: bool | None = None


# --- Read Schemas (for response body) ---
class ListingReadBase(ListingBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    average_rating: float | None = None
    images: List[ImageRead] = []

    model_config = ConfigDict(from_attributes=True)


class HotelRead(ListingReadBase):
    type: Literal[ListingType.HOTEL]
    star_rating: int


class ApartmentRead(ListingReadBase):
    type: Literal[ListingType.APARTMENT]
    number_of_bedrooms: int
    number_of_bathrooms: int
    max_guests: int


class HostelRead(ListingReadBase):
    type: Literal[ListingType.HOSTEL]
    dorm_bed_count: int | None
    private_room_count: int | None


class GuesthouseRead(ListingReadBase):
    type: Literal[ListingType.GUESTHOUSE]
    number_of_rooms: int
    host_on_site: bool


# A discriminated union for Pydantic to serialize the response with
ListingRead = Annotated[
    Union[HotelRead, ApartmentRead, GuesthouseRead, HostelRead],
    Field(discriminator="type")
]
