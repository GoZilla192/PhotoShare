from __future__ import annotations

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.photo import Photo
from app.models.roles import UserRole
from app.models.user import User
from app.repository.photos_repository import PhotoRepository
from app.repository.tags_repository import TagRepository
from app.service.cloudinary_service import CloudinaryService


class PhotoService:
    def __init__(self, session: AsyncSession,
                 photos_repo: PhotoRepository,
                 cloudinary_client: CloudinaryService,
                 tags_repo: TagRepository,):
        self.session = session
        self.photos = photos_repo
        self.cloudinary = cloudinary_client
        self.tags = tags_repo

    async def create_photo(
            self,
            *,
            user_id: int,
            file: bytes,
            photo_unique_url: str,
            description: str | None = None,
            tags: list[str] | None = None,
    ) -> Photo:
        # upload to cloudinary first
        upload = self.cloudinary.upload_photo(file)
        public_id = upload["public_id"]

        # persist in DB
        photo = Photo(
            user_id=user_id,
            cloudinary_public_id=public_id,
            photo_unique_url=photo_unique_url,
            description=description,
        )
        try:
            async with self.session.begin():
                await self.photos.add(photo)
                # щоб мати photo.id для tagging
                await self.session.flush()
        except Exception:
            # best-effort cleanup in cloudinary to avoid orphan files
            try:
                self.cloudinary.delete_photo(upload["public_id"])
            except Exception:
                pass
            raise

        # optional tags
        if tags:
            # enforce max=5 на рівні репозиторію
            await self.tags.set_tags_for_photo(photo.id, tags, max_tags=5)

        return photo

    async def get_photo(self, photo_id: int) -> Photo:
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")
        return photo

    async def get_photo_by_unique_url(self, unique_url: str) -> Photo:
        photo = await self.photos.get_by_unique_url(unique_url)
        if not photo:
            raise NotFoundError("Photo not found")
        return photo

    async def update_description(
        self,
        photo_id: int,
        description: str | None,
        current_user: User,
    ) -> Photo:
        photo = await self.get_photo(photo_id)
        self.ensure_owner_or_admin(current_user, photo.user_id)
        async with self.session.begin():
            updated = await self.photos.update_description(photo_id, description or "")
        if not updated:
            raise NotFoundError("Photo not found")
        return updated

    async def delete_photo(self, photo_id: int, current_user: User) -> None:
        photo = await self.get_photo(photo_id)
        self.ensure_owner_or_admin(current_user, photo.user_id)

        # delete in DB first (or cloudinary first — дискусійно)
        async with self.session.begin():
            ok = await self.photos.delete_by_id(photo_id)
        if ok:
            # best-effort cloudinary cleanup
            try:
                self.cloudinary.delete_photo(photo.cloudinary_public_id)
            except Exception:
                pass

    async def list_by_user(self, user_id: int, *, limit: int = 50, offset: int = 0) -> list[Photo]:
        return await self.photos.list_by_user(user_id=user_id, limit=limit, offset=offset)

    async def count_by_user(self, user_id: int) -> int:
        return await self.photos.count_by_user(user_id)

    def ensure_owner_or_admin(self, current_user: User, photo_user_id: int) -> None:
        if current_user.role == UserRole.admin:
            return
        if photo_user_id != current_user.id:
            raise PermissionDeniedError("Insufficient permissions")

    async def search_photos(
            self,
            *,
            q: str | None = None,
            tag: str | None = None,
            min_rating: float | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
            sort: str = "newest",
            limit: int = 50,
            offset: int = 0,
    ) -> tuple[list[Photo], int]:
        items = await self.photos.search(
            q=q,
            tag=tag,
            min_rating=min_rating,
            date_from=date_from,
            date_to=date_to,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        total = await self.photos.count_search(
            q=q,
            tag=tag,
            min_rating=min_rating,
            date_from=date_from,
            date_to=date_to,
        )
        return items, total