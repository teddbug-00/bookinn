import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Retrieves a user by their email address."""
    query = select(User).where(User.email == email)
    return (await db.execute(query)).scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    """Retrieves a user by their user ID. """
    query = select(User).where(User.id == user_id)
    return (await db.execute(query)).scalar_one_or_none()
