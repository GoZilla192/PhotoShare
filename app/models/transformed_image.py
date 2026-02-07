from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.mixins import CreatedAtMixin


class TransformedImage(Base, CreatedAtMixin):
    __tablename__ = "transformed_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"),
        nullable=False
    )

    transformation: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Відносини
    photo: Mapped["Photo"] = relationship(back_populates="transformed_images")

    public_links: Mapped[list["PublicLink"]] = relationship(
        back_populates="transformed_image",
        cascade = "all, delete-orphan",
        passive_deletes = True,
        )
