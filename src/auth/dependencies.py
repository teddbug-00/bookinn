from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import CredentialsException
from src.auth.security import token_manager, oauth2_scheme
from src.config import settings
from src.database import get_db_session
from src.users.dependencies import get_user_by_id
from src.users.models import User


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_db_session)
) -> User:
    """Decodes JWT token, retrieves user from DB, and provides it as a dependency."""
    payload = token_manager.decode_token(token, settings.ACCESS_SECRET_KEY)

    if payload.token_type != "access":
        raise CredentialsException()

    user_id = payload.sub
    user = await get_user_by_id(session, user_id=user_id)
    if not user:
        raise CredentialsException()

    return user
