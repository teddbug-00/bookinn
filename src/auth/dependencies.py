from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.exceptions import CredentialsException, NotEnoughPermissionsException
from src.config import settings
from src.database import get_db_session
from src.users import repository as user_repository
from src.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def _get_user_from_token(token: str, session: AsyncSession) -> User:
    """
    Private helper to decode an access token and fetch the corresponding user
    """
    payload = auth_utils.decode_token(token, settings.ACCESS_SECRET_KEY)

    if payload.token_type != "access":
        raise CredentialsException()

    user_id = payload.sub
    user = await user_repository.get_user_by_id(session, user_id=user_id)
    if not user:
        raise CredentialsException()

    return user


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency to get the currently authenticated user from a token."""
    return await _get_user_from_token(token, session)


async def get_current_admin_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency to get the current user, ensuring they have admin privileges."""
    user = await _get_user_from_token(token, session)

    if not user.is_admin:
        raise NotEnoughPermissionsException()

    return user
