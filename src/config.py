from typing import cast

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings


class MainConfig(BaseSettings):
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_ECHO_LOG: bool = True  # Set this to false in production

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Construct the asynchronous database URL."""
        url = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # Cast the string to PostgresDsn to satisfy static type checkers.
        # Pydantic uses the '-> PostgresDsn' return hint for runtime validation.
        return cast(PostgresDsn, url)


settings = MainConfig()
