from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base
from models.enums import DeliveryStatus


class Delivery(Base):
    __tablename__ = "deliveries"

    __table_args__ = (
        UniqueConstraint(
            "post_id",
            "destination_id",
            name="uq_post_destination"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus),
        default=DeliveryStatus.PENDING,
        nullable=False,
        index=True
    )

    telegram_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    post = relationship(
        "Post",
        backref="deliveries"
    )

    destination = relationship(
        "Destination",
        backref="deliveries"
    )
