import datetime
import uuid
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from src.listings.enums import ListingType


class BookingBase(BaseModel):
    """Base schema for creating a booking."""
    listing_id: uuid.UUID
    check_in_date: datetime.date


class ApartmentBookingCreate(BookingBase):
    """Schema for creating a new apartment booking."""
    type: Literal[ListingType.APARTMENT]
    number_of_months: int


# A discriminated union for FastAPI to validate the request body against
BookingCreate = Annotated[
    Union[ApartmentBookingCreate],
    Field(discriminator="type")
]


class BookingReadBase(BaseModel):
    """Base schema for reading booking data."""
    id: uuid.UUID
    check_in_date: datetime.date
    check_out_date: datetime.date
    total_price: float
    status: str
    user_id: uuid.UUID
    listing_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class ApartmentBookingRead(BookingReadBase):
    type: Literal[ListingType.APARTMENT]


# A discriminated union for Pydantic to serialize the response with
BookingRead = Annotated[
    Union[ApartmentBookingRead],
    Field(discriminator="type")
]
