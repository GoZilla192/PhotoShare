from __future__ import annotations
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy

from app.models.photo_tags import PhotoTag
from app.models.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    # many-to-many
    photo_tags: Mapped[list[PhotoTag]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan"
    )
    photos: list[Photo] = association_proxy("photo_tags", "photo")
