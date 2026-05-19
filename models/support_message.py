from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base
from models.enums import SupportStatus


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    telegram_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    message_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[SupportStatus] = mapped_column(
        Enum(SupportStatus),
        default=SupportStatus.OPEN,
        nullable=False,
        index=True
    )

    admin_reply: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        backref="support_messages"
    )
