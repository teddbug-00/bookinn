import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from jose import jwt, JWTError, ExpiredSignatureError

from src.auth.exceptions import CredentialsException, TokenExpiredException
from src.auth.schemas import TokenPayload
from src.config import settings

# --- Password Utilities ---
_ph = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    try:
        _ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, InvalidHash):
        # InvalidHash could be raised if the hash is malformed.
        # In either case, it's a failed verification.
        return False


def get_password_hash(password: str) -> str:
    """Hashes a plain-text password using Argon2."""
    return _ph.hash(password)


# --- Token Utilities ---
def create_access_token(user_id: uuid.UUID) -> str:
    """Creates a new access token using configured settings."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(user_id), "token_type": "access"}
    return jwt.encode(to_encode, settings.ACCESS_SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: uuid.UUID) -> str:
    """Creates a new refresh token using configured settings."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(user_id), "token_type": "refresh"}
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm="HS256")


def decode_token(token: str, secret_key: str) -> TokenPayload:
    """
    Decodes a JWT token and returns the payload.
    Raises exceptions for invalid, malformed, or expired tokens.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return TokenPayload(**payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        # This covers all other JWT exceptions
        raise CredentialsException()
