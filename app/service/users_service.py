from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError, ConflictError, NotFoundError
from app.models.user import User
from app.models.roles import UserRole
from app.repository.users_repository import UserRepository

from app.schemas.user_profile_shema import (
    UserPublicProfile,
    UserMeProfile,
    UserMeUpdateRequest,
    UserBanResponse,
)

class UserService:
    def __init__(
        self,
        session: AsyncSession,
        users_repo: UserRepository,
        photos_repo=None,  # опціонально: щоб порахувати photos_count
    ):
        self.session = session
        self.users = users_repo
        self.photos = photos_repo

    async def get_public_profile_by_username(self, username: str) -> UserPublicProfile:
        user = await self.users.get_by_username(username)
        if not user:
            raise NotFoundError("User not found")

        photos_count = 0
        if self.photos is not None:
            photos_count = await self.photos.count_by_user(user.id)

        data = UserPublicProfile.model_validate(user, from_attributes=True)
        return data.model_copy(update={"photos_count": photos_count})

    async def get_me(self, current_user: User) -> UserMeProfile:
        photos_count = 0
        if self.photos is not None:
            photos_count = await self.photos.count_by_user(current_user.id)

        data = UserMeProfile.model_validate(current_user, from_attributes=True)
        return data.model_copy(update={"photos_count": photos_count})

    async def update_me(self, *, current_user: User, req: UserMeUpdateRequest) -> UserMeProfile:
        if not current_user.is_active:
            raise PermissionDeniedError("User is inactive")

        # Унікальність username/email — 409 замість 500
        if req.username and req.username != current_user.username:
            existing = await self.users.get_by_username(req.username)
            if existing and existing.id != current_user.id:
                raise ConflictError("Username already taken")

        if req.email and req.email != current_user.email:
            existing = await self.users.get_by_email(req.email)
            if existing and existing.id != current_user.id:
                raise ConflictError("Email already taken")

        async with self.session.begin():
            updated = await self.users.update_profile_fields(
                current_user.id,
                username=req.username,
                email=req.email,
            )
        if not updated:
            raise NotFoundError("User not found")

        photos_count = 0
        if self.photos is not None:
            photos_count = await self.photos.count_by_user(updated.id)

        data = UserMeProfile.model_validate(updated, from_attributes=True)
        return data.model_copy(update={"photos_count": photos_count})

    async def ban_user(self, *, target_user_id: int, current_user: User) -> UserBanResponse:
        self._require_admin(current_user)

        async with self.session.begin():
            ok = await self.users.set_is_active(target_user_id, False)

        if not ok:
            raise NotFoundError("User not found")

        return UserBanResponse(user_id=target_user_id, is_active=False)

    async def unban_user(self, *, target_user_id: int, current_user: User) -> UserBanResponse:
        self._require_admin(current_user)

        async with self.session.begin():
            ok = await self.users.set_is_active(target_user_id, True)

        if not ok:
            raise NotFoundError("User not found")

        return UserBanResponse(user_id=target_user_id, is_active=True)

    async def set_role(self, *, target_user_id: int, role: UserRole, current_user: User) -> None:
        self._require_admin(current_user)

        async with self.session.begin():
            target = await self.users.get_by_id(target_user_id)
            if not target:
                raise NotFoundError("User not found")
            target.role = role
            await self.session.flush()

    @staticmethod
    def _require_admin(current_user: User) -> None:
        if current_user.role != UserRole.admin:
            raise PermissionDeniedError("Admin role required")

