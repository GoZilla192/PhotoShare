from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models import Photo, Tag


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id"),
        primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id"),
        primary_key=True
    )

    # relations
    photo: Mapped["Photo"] = relationship(back_populates="photo_tags")
    tag:   Mapped["Tag"]   = relationship(back_populates="photo_tags")
