from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.exceptions import IncorrectEmailOrPasswordException, CredentialsException
from src.auth.schemas import Token
from src.config import settings
from src.users import repository as user_repository


async def authenticate_user_and_get_tokens(
        email: str, password: str, session: AsyncSession
) -> Token:
    """
    Authenticates a user by checking their credentials and returns a new token pair.
    """
    user = await user_repository.get_user_by_email(session, email=email)
    if not user or not auth_utils.verify_password(password, user.hashed_password):
        raise IncorrectEmailOrPasswordException()

    access_token = auth_utils.create_access_token(user_id=user.id)
    refresh_token = auth_utils.create_refresh_token(user_id=user.id)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def refresh_tokens(refresh_token: str, session: AsyncSession) -> Token:
    """
    Validates a refresh token, ensures the user exists, and issues a new token pair.
    """
    payload = auth_utils.decode_token(refresh_token, settings.REFRESH_SECRET_KEY)
    user = await user_repository.get_user_by_id(session, user_id=payload.sub)
    if not user:
        raise CredentialsException()

    new_access_token = auth_utils.create_access_token(user_id=user.id)
    new_refresh_token = auth_utils.create_refresh_token(user_id=user.id)
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
