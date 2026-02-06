from __future__ import annotations

from sqlalchemy import Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True)

    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # relationships
    photo: Mapped["Photo"] = relationship(
        back_populates="ratings"
    )

    user: Mapped["User"] = relationship(
        back_populates="ratings"
    )

    __table_args__ = (
        UniqueConstraint(
            "photo_id",
            "user_id",
            name="uix_rating_photo_user"
        ),
        CheckConstraint(
            "value BETWEEN 1 AND 5",
            name="ck_rating_value_range"
        ),
    )