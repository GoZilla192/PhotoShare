from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id"), nullable=False)
    user_id:  Mapped[int] = mapped_column(ForeignKey("users.id"),  nullable=False)

    text: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # relations
    photo: Mapped["Photo"] = relationship(back_populates="comments")
    user:  Mapped["User"]  = relationship(back_populates="comments")
