import datetime
import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.listings.enums import ListingType


class GuesthouseBookingCreate(BaseModel):
    """Schema for creating a new guesthouse booking."""
    type: Literal[ListingType.GUESTHOUSE]
    listing_id: uuid.UUID
    check_in_date: datetime.date
    check_out_date: datetime.date
    number_of_rooms: int = Field(1, gt=0)

    @model_validator(mode='after')
    def check_dates(self) -> 'GuesthouseBookingCreate':
        if self.check_in_date >= self.check_out_date:
            raise ValueError("Check-out date must be after check-in date.")
        return self


class GuesthouseBookingRead(BaseModel):
    type: Literal[ListingType.GUESTHOUSE]
    id: uuid.UUID
    check_in_date: datetime.date
    check_out_date: datetime.date
    total_price: float
    status: str
    user_id: uuid.UUID
    listing_id: uuid.UUID
    number_of_rooms_booked: int

    model_config = ConfigDict(from_attributes=True)
