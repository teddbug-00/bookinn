from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.config import settings

# Base class for all ORM models
Base = declarative_base()


class Database:
    """
    Manages the database connection, engine, and session creation.
    """

    def __init__(self, db_url: str, echo: bool = False):
        self.engine = create_async_engine(
            db_url,
            echo=echo,
            pool_pre_ping=True,
        )

        # The session factory creates new session objects when called.
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def disconnect(self):
        """Closes all connections in the connection pool."""
        await self.engine.dispose()

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependency for providing a database session for a request."""
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()


db = Database(str(settings.DATABASE_URL), echo=settings.DB_ECHO_LOG)

# Create a standalone dependency function
get_db_session = db.get_db
