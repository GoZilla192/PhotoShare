from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError, PermissionDeniedError
from app.models.photo import Photo
from app.models.roles import UserRole
from app.models.user import User
from app.repository.photos_repository import PhotoRepository
from app.service.cloudinary_service import CloudinaryService


class PhotoService:
    def __init__(self, session: AsyncSession,
                 photos_repo: PhotoRepository,
                 cloudinary_client: CloudinaryService):
        self.session = session
        self.photos = photos_repo
        self.cloudinary = cloudinary_client

    async def create_photo(
            self,
            user_id: int,
            file,
            photo_unique_url: str,
            description: str | None = None
    ) -> Photo:
        # upload to cloudinary first
        upload = self.cloudinary.upload_photo(file)  # sync ok for MVP

        # persist in DB
        photo = Photo(
            user_id=user_id,
            photo_url=upload["url"],
            cloudinary_public_id=upload["public_id"],
            photo_unique_url=photo_unique_url,
            description=description,
        )
        try:
            async with self.session.begin():
                await self.photos.add(photo)
        except Exception:
            # best-effort cleanup in cloudinary to avoid orphan files
            try:
                self.cloudinary.delete_photo(upload["public_id"])
            except Exception:
                pass
            raise

        return photo

    async def get_photo(self, photo_id: int) -> Photo:
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")
        return photo

    async def get_photo_by_unique_url(self, unique_url: str) -> Photo:
        photo = await self.photos.get_by_unique_url(unique_url)
        if photo:
            raise NotFoundError("Photo not found")
        return photo

    async def update_description(
        self,
        photo_id: int,
        description: str | None,
        current_user: User,
    ) -> Photo:
        photo = await self.get_photo(photo_id)
        self._ensure_owner_or_admin(current_user, photo)
        async with self.session.begin():
            updated = await self.photos.update_description(photo_id, description or "")
        if not updated:
            raise NotFoundError("Photo not found")
        return updated

    async def delete_photo(self, photo_id: int, current_user: User) -> None:
        photo = await self.get_photo(photo_id)
        self._ensure_owner_or_admin(current_user, photo)

        # delete in DB first (or cloudinary first — дискусійно)
        async with self.session.begin():
            ok = await self.photos.delete_by_id(photo_id)
        if ok:
            # best-effort cloudinary cleanup
            try:
                self.cloudinary.delete_photo(photo.cloudinary_public_id)
            except Exception:
                pass

    async def list_by_user(self, user_id: int) -> list[Photo]:
        return await self.photos.list_by_user(user_id)

    async def count_by_user(self, user_id: int) -> int:
        return await self.photos.count_by_user(user_id)

    def _ensure_owner_or_admin(self, current_user: User, photo: Photo) -> None:
        if current_user.role == UserRole.admin:
            return
        if photo.user_id != current_user.id:
            raise PermissionDeniedError("Insufficient permissions")