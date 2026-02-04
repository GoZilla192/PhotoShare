from __future__ import annotations
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from app.models.photo_tags import PhotoTag
from app.models.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    photo_unique_url: Mapped[str] = mapped_column(nullable=False, unique=True) # unique url on photo
    photo_url: Mapped[str] = mapped_column(nullable=False) # path to photo on OS
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
    photo_tags: Mapped[List["PhotoTag"]] = relationship("PhotoTag", back_populates="photo")
    tags: List["Tag"] = association_proxy("photo_tags", "tag")
