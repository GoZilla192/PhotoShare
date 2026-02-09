from __future__ import annotations

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin
from app.models.photo_tags import PhotoTag
from app.models.base import Base


class Photo(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    photo_unique_url: Mapped[str] = mapped_column(nullable=False, unique=True) # unique url on photo
    cloudinary_public_id: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)

    # one-to-many
    ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="photo",
        cascade="all, delete-orphan",
        passive_deletes = True,
    )

    # many-to-one / one-to-many
    user: Mapped["User"] = relationship(back_populates="photos")

    comments: Mapped[List["Comment"]] = relationship(
        "Comment",
        back_populates="photo",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    transformed_images: Mapped[List["TransformedImage"]] = relationship(
        "TransformedImage",
        back_populates="photo",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # many-to-many
    photo_tags: Mapped[List["PhotoTag"]] = relationship(
        "PhotoTag",
        back_populates="photo",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags: List["Tag"] = association_proxy("photo_tags", "tag")