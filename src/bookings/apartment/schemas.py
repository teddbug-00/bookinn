import datetime
import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict

from src.listings.enums import ListingType


class ApartmentBookingCreate(BaseModel):
    """Schema for creating a new apartment booking."""
    type: Literal[ListingType.APARTMENT]
    listing_id: uuid.UUID
    check_in_date: datetime.date
    number_of_months: int


class ApartmentBookingRead(BaseModel):
    type: Literal[ListingType.APARTMENT]
    id: uuid.UUID
    check_in_date: datetime.date
    check_out_date: datetime.date
    total_price: float
    status: str
    user_id: uuid.UUID
    listing_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
