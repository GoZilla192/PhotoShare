from __future__ import annotations

from sqlalchemy import Enum as SAEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import IsActiveMixin, CreatedAtMixin, UpdatedAtMixin
from app.models.roles import UserRole
from app.models.base import Base


class User(Base, IsActiveMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.user,
        server_default=UserRole.user.value,
    )

    # one-to-many
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes = True
    )

    photos: Mapped[list["Photo"]] = relationship(
        back_populates="user"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="user"
    )