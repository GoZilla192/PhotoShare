from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin


class Comment(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id",ondelete="CASCADE"), nullable=False)
    user_id:  Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),  nullable=False)

    text: Mapped[str] = mapped_column(nullable=False)

    # relations
    photo: Mapped["Photo"] = relationship(back_populates="comments")
    user:  Mapped["User"]  = relationship(back_populates="comments")
