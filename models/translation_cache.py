from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.base import Base


class TranslationCache(Base):

    __tablename__ = "translation_cache"

    __table_args__ = (
        UniqueConstraint(
            "content_hash",
            "target_language",
            name="uq_translation_cache",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    source_language: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )

    target_language: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )

    original_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    translated_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
