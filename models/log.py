from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base
from models.enums import LogLevel


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel),
        nullable=False,
        index=True
    )

    module: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
