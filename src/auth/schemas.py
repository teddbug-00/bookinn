import uuid

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: uuid.UUID
    token_type: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
