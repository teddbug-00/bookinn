import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError

from src.auth.exceptions import CredentialsException, TokenExpiredException
from src.auth.schemas import TokenPayload
from src.config import settings


class PasswordManager:
    """Handles all password-related operations like hashing and verification."""

    def __init__(self):
        self.ph = PasswordHasher()

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain-text password against a hashed one."""
        try:
            self.ph.verify(hashed_password, plain_password)
            return True
        except (VerifyMismatchError, InvalidHash):
            # InvalidHash could be raised if the hash is malformed.
            # In either case, it's a failed verification.
            return False

    def get_hash(self, password: str) -> str:
        """Hashes a plain-text password using Argon2."""
        return self.ph.hash(password)


class TokenManager:
    """Handles all JWT-related operations."""

    def __init__(self, settings_obj):
        self.settings = settings_obj

    def _create_token(
            self, user_id: uuid.UUID, expires_delta: timedelta, secret_key: str, token_type: str
    ) -> str:
        """Generic token creation helper."""
        to_encode = TokenPayload(sub=user_id, token_type=token_type).model_dump(mode="json")
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=self.settings.ALGORITHM)
        return encoded_jwt

    def create_access_token(self, user_id: uuid.UUID) -> str:
        """Creates a new JWT access token."""
        expires_delta = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return self._create_token(
            user_id=user_id,
            expires_delta=expires_delta,
            secret_key=self.settings.ACCESS_SECRET_KEY,
            token_type="access",
        )

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """Creates a new JWT refresh token."""
        expires_delta = timedelta(minutes=self.settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        return self._create_token(
            user_id=user_id,
            expires_delta=expires_delta,
            secret_key=self.settings.REFRESH_SECRET_KEY,
            token_type="refresh",
        )

    def decode_token(self, token: str, secret_key: str) -> TokenPayload:
        """Decodes a JWT token and returns its payload, handling errors."""
        try:
            payload_data = jwt.decode(
                token, secret_key, algorithms=[self.settings.ALGORITHM]
            )
            return TokenPayload(**payload_data)
        except ExpiredSignatureError:
            raise TokenExpiredException()
        except (JWTError, ValueError):  # ValueError for malformed UUID
            raise CredentialsException()


# Create singleton instances for the application to use
password_manager = PasswordManager()
token_manager = TokenManager(settings)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
