from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base


class SourceCache(Base):
    __tablename__ = "source_cache"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True
    )

    etag: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    last_modified: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    last_success_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    last_error_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
