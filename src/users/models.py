import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(sa.String(length=255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=50), nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String, nullable=False)

    def __str__(self):
        return str(self.id)
