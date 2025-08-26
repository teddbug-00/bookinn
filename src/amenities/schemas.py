import uuid

from pydantic import BaseModel, ConfigDict, Field


class AmenityBase(BaseModel):
    name: str
    icon_url: str | None = Field(None, max_length=2048)



class AmenityCreate(AmenityBase):
    pass


class AmenityUpdate(BaseModel):
    name: str | None = None
    icon_url: str | None = Field(None, max_length=2048)


class AmenityRead(AmenityBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
