import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class ApartmentBookingCreate(BaseModel):
    """Schema for creating a new apartment booking."""
    listing_id: uuid.UUID
    check_in_date: datetime.date
    number_of_months: int


class ApartmentBookingRead(BaseModel):
    id: uuid.UUID
    check_in_date: datetime.date
    check_out_date: datetime.date
    total_price: float
    status: str
    user_id: uuid.UUID
    listing_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
