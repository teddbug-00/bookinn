import uuid

from pydantic import BaseModel, ConfigDict


class ImageCreate(BaseModel):
    """Schema for creating an image record in the database."""
    url: str
    is_thumbnail: bool
    listing_id: uuid.UUID


class ImageRead(BaseModel):
    """Schema for reading image data."""
    id: uuid.UUID
    url: str
    is_thumbnail: bool

    model_config = ConfigDict(from_attributes=True)
