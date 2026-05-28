from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base


class SourceHealth(Base):

    __tablename__ = "source_health"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pack_sources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    last_success_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_failure_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_error: Mapped[
        str | None
    ] = mapped_column(
        String(1000),
        nullable=True,
    )

    success_count: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            nullable=False,
        )
    )

    failure_count: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            nullable=False,
        )
    )

    average_score: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            nullable=False,
        )
    )

    last_score: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            nullable=False,
        )
    )
