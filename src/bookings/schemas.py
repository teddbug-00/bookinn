import datetime
import uuid
from typing import Annotated, Union

from pydantic import BaseModel, ConfigDict, Field

from src.bookings.apartment.schemas import ApartmentBookingCreate, ApartmentBookingRead
from src.bookings.guesthouse.schemas import GuesthouseBookingCreate, GuesthouseBookingRead


class BookingBase(BaseModel):
    """Base schema for creating a booking."""
    listing_id: uuid.UUID
    check_in_date: datetime.date


# A discriminated union for FastAPI to validate the request body against
BookingCreate = Annotated[
    Union[ApartmentBookingCreate, GuesthouseBookingCreate],
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


# A discriminated union for Pydantic to serialize the response with
BookingRead = Annotated[
    Union[ApartmentBookingRead, GuesthouseBookingRead],
    Field(discriminator="type")
]
