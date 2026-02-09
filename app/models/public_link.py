from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.mixins import CreatedAtMixin


class PublicLink(Base, CreatedAtMixin):
    __tablename__ = "public_links"

    id: Mapped[int] = mapped_column(primary_key=True)

    transformed_image_id: Mapped[int] = mapped_column(
        ForeignKey("transformed_images.id", ondelete="CASCADE"),
        nullable=False
    )

    uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False
    )

    qr_code_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    # relations
    transformed_image: Mapped["TransformedImage"] = relationship(
        back_populates="public_links"
    )
