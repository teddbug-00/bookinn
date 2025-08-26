import uuid

from pydantic import BaseModel, ConfigDict


class ImageRead(BaseModel):
    """Schema for reading image data."""
    id: uuid.UUID
    url: str
    is_thumbnail: bool

    model_config = ConfigDict(from_attributes=True)
