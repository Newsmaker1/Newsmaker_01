from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base
from models.enums import PostStatus


class Post(Base):
    __tablename__ = "posts"

    __table_args__ = (
        UniqueConstraint(
            "source_url",
            name="uq_post_source_url"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    pack_id: Mapped[int] = mapped_column(
        ForeignKey("source_packs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True
    )

    source_domain: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    translated_title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    translated_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    telegram_file_id: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )

    url_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    similarity_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus),
        default=PostStatus.NEW,
        nullable=False,
        index=True
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    processing_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    pack = relationship(
        "SourcePack",
        backref="posts"
    )
