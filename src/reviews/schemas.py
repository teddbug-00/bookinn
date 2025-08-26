import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ReviewerRead(BaseModel):
    """Schema for displaying basic reviewer information within a review."""
    id: uuid.UUID
    name: str
    profile_picture_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: uuid.UUID
    created_at: datetime.datetime
    reviewer_id: uuid.UUID
    listing_id: uuid.UUID
    reviewer: ReviewerRead

    model_config = ConfigDict(from_attributes=True)
