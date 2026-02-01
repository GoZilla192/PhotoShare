from __future__ import annotations
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    photos: Mapped[list["Photo"]] = relationship(
        "Photo",
        secondary=PhotoTag,
        back_populates="tags"
    )
