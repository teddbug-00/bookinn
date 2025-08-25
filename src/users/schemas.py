import uuid
from datetime import date

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    date_of_birth: date


class UserUpdate(BaseModel):
    name: str | None = None
    date_of_birth: date | None = None
    profile_picture_url: str | None = None

# Properties to return to client
class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    date_of_birth: date
    profile_picture_url: str | None

    class Config:
        from_attributes = True
