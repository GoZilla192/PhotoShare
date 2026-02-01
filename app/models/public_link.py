from __future__ import annotations
from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class PublicLink(Base):
    __tablename__ = "public_links"

    id: Mapped[int] = mapped_column(primary_key=True)

    transformed_image_id: Mapped[int] = mapped_column(
        ForeignKey("transformed_images.id"),
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

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,           # або lambda: datetime.utcnow()
        nullable=False
    )

    # relations
    transformed_image: Mapped["TransformedImage"] = relationship(
        back_populates="public_links"
    )
