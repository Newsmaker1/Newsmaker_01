from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.base import Base


class PackDestination(Base):

    __tablename__ = "pack_destinations"

    __table_args__ = (
        UniqueConstraint(
            "pack_id",
            "destination_id",
            name="uq_pack_destination",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    pack_id: Mapped[int] = mapped_column(
        ForeignKey(
            "source_packs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey(
            "destinations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    pack = relationship(
        "SourcePack",
        backref="pack_destinations",
    )

    destination = relationship(
        "Destination",
        backref="pack_destinations",
    )
