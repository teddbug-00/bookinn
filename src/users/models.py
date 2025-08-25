import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(sa.String(length=255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(sa.Date, nullable=False)
    profile_picture_url: Mapped[str | None] = mapped_column(sa.String(length=2048), nullable=True)
    hashed_password: Mapped[str] = mapped_column(sa.String, nullable=False)

    def __str__(self):
        return str(self.id)
