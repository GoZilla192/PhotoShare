from __future__ import annotations
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.photo_tags import photo_tags
from app.models import Photo


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
        secondary=photo_tags,
        back_populates="tags"
    )
