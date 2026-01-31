from __future__ import annotations
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.photo_tags import photo_tags
from app.models import Tag, User, Comment, TransformedImage


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    image_url: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # many-to-one / one-to-many
    user: Mapped["User"] = relationship(back_populates="photos")

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="photo"
    )

    transformed_images: Mapped[List["TransformedImage"]] = relationship(
        back_populates="photo"
    )

    # many-to-many
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=photo_tags,
        back_populates="photos"
    )
