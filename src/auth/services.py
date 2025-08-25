from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import IncorrectEmailOrPasswordException, CredentialsException
from src.auth.schemas import Token
from src.auth.security import password_manager, token_manager
from src.config import settings
from src.users.dependencies import get_user_by_email, get_user_by_id


async def authenticate_user_and_get_tokens(
        email: str, password: str, session: AsyncSession
) -> Token:
    """
    Authenticates a user by checking their credentials and returns a new token pair.
    """
    user = await get_user_by_email(session, email=email)
    if not user or not password_manager.verify(password, user.hashed_password):
        raise IncorrectEmailOrPasswordException()

    access_token = token_manager.create_access_token(user_id=user.id)
    refresh_token = token_manager.create_refresh_token(user_id=user.id)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def refresh_tokens(refresh_token: str, session: AsyncSession) -> Token:
    """
    Validates a refresh token, ensures the user exists, and issues a new token pair.
    """
    payload = token_manager.decode_token(refresh_token, settings.REFRESH_SECRET_KEY)

    # Ensure the user from the token still exists.
    user = await get_user_by_id(session, user_id=payload.sub)
    if not user:
        raise CredentialsException()

    new_access_token = token_manager.create_access_token(user_id=user.id)
    new_refresh_token = token_manager.create_refresh_token(user_id=user.id)
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
