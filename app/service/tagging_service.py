from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.roles import UserRole
from app.models.user import User
from app.repository.photos_repository import PhotoRepository
from app.repository.tags_repository import TagRepository


class TaggingService:
    def __init__(self,
                 session: AsyncSession,
                 tags_repo: TagRepository,
                 photos_repo: PhotoRepository):
        self.session = session
        self.tags = tags_repo
        self.photos = photos_repo

    async def get_photo_tags(self, *, photo_id: int) -> list[str]:
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")
        return await self.tags.list_tag_names_for_photo(photo_id)

    async def set_photo_tags(self, *, photo_id: int, tag_names: list[str], current_user: User) -> list[str]:
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")

        # owner or admin
        if current_user.role != UserRole.admin and photo.user_id != current_user.id:
            raise PermissionDeniedError("Insufficient permissions")

        async with self.session.begin():
            return await self.tags.set_tags_for_photo(photo_id, tag_names, max_tags=5)

    def _parse_tags_csv(self, tags: str | None) -> list[str] | None:
        if not tags:
            return None
        items = [t.strip() for t in tags.split(",")]
        items = [t for t in items if t]  # drop empty
        if not items:
            return None
        # safety clamp; основний ліміт також enforced в репо/сервісі
        return items[:5]

    async def get_tag_cloud(self, *, limit: int = 50, offset: int = 0) -> list[dict]:
        items = await self.tags.list_cloud(limit=limit, offset=offset)
        # Повертаємо UI-friendly структуру, без ORM.
        return [{"name": name, "count": count} for name, count in items]

