from __future__ import annotations
from datetime import datetime
from typing import List
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from app.models.photo_tags import PhotoTag
from app.models.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    url: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
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
    photo_tags: Mapped[List["PhotoTag"]] = relationship("PhotoTag", back_populates="photo")
    tags: List["Tag"] = association_proxy("photo_tags", "tag")
