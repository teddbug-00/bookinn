import uuid

from pydantic import BaseModel, ConfigDict


class AmenityBase(BaseModel):
    name: str


class AmenityCreate(AmenityBase):
    pass


class AmenityUpdate(BaseModel):
    name: str | None = None


class AmenityRead(AmenityBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
