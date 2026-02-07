from app.exceptions import NotFoundError, PermissionDeniedError
from app.models.photo import Photo
from app.models.roles import UserRole
from app.models.user import User
from app.repository.photos import PhotoRepository
from app.service.cloudinary import upload_photo, delete_photo


class PhotoService:
    def __init__(self, photo_repo: PhotoRepository) -> None:
        self._photo_repo = photo_repo

    async def create_photo(
        self,
        user_id: int,
        file,
        photo_unique_url: str,
        description: str | None = None,
    ) -> Photo:
        upload_result = upload_photo(file)

        return await self._photo_repo.create(
            user_id=user_id,
            photo_url=upload_result["url"],
            cloudinary_public_id=upload_result["public_id"],
            photo_unique_url=photo_unique_url,
            description=description,
        )

    async def get_photo(self, photo_id: int) -> Photo:
        photo = await self._photo_repo.get(photo_id)
        if photo is None:
            raise NotFoundError("Photo not found")
        return photo

    async def get_photo_by_unique_url(self, photo_unique_url: str) -> Photo:
        photo = await self._photo_repo.get_by_unique_url(photo_unique_url)
        if photo is None:
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
        return await self._photo_repo.update_description(photo, description)

    async def delete_photo(self, photo_id: int, current_user: User) -> None:
        photo = await self.get_photo(photo_id)
        self._ensure_owner_or_admin(current_user, photo)
        delete_photo(photo.cloudinary_public_id) # Cloudinary
        await self._photo_repo.delete(photo)

    async def list_by_user(self, user_id: int) -> list[Photo]:
        return await self._photo_repo.list_by_user(user_id)

    async def search_photos(self, *, current_user = User, keyword: str | None = None, tag: str | None = None, user_id: int | None = None, date_order: str | None = None) -> list[Photo]:
        if user_id is not None:
            if current_user.role not in (UserRole.admin, UserRole.moderator):
                raise PermissionDeniedError("Only admin or moderator can search by user")
        return await self._photo_repo.search(
            keyword=keyword,
            tag=tag,
            user_id=user_id,
            date_order=date_order
        )

    def _ensure_owner_or_admin(self, current_user: User, photo: Photo) -> None:
        if current_user.role == UserRole.admin:
            return
        if photo.user_id != current_user.id:
            raise PermissionDeniedError("Insufficient permissions")