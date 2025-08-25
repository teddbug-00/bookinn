from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import password_manager
from src.users.dependencies import get_user_by_email
from src.users.exceptions import UserAlreadyExistsException
from src.users.models import User
from src.users.schemas import UserCreate


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Creates a new user in the database after checking for duplicates."""
    # Fail fast if the email is already being used
    if await get_user_by_email(db, user_in.email):
        raise UserAlreadyExistsException()

    hashed_password = password_manager.get_hash(user_in.password)
    db_user = User(email=user_in.email, name=user_in.name, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
