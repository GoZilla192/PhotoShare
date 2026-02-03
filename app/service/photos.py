from app.exceptions import NotFoundError, PermissionDeniedError
from app.models.photo import Photo
from app.models.roles import UserRole
from app.models.user import User
from app.repository.photos import PhotoRepository


class PhotoService:
    def __init__(self, photo_repo: PhotoRepository) -> None:
        self._photo_repo = photo_repo

    async def create_photo(
        self,
        owner_id: int,
        url: str,
        description: str | None = None,
    ) -> Photo:
        photo = Photo(
            owner_id=owner_id,
            url=url,
            description=description,
        )
        return await self._photo_repo.create(photo)

    async def get_photo(self, photo_id: int) -> Photo:
        photo = await self._photo_repo.get(photo_id)
        if photo is None:
            raise NotFoundError("Photo not found")
        return photo

    async def get_photo_by_url(self, url: str) -> Photo:
        photo = await self._photo_repo.get_by_url(url)
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
        await self._photo_repo.delete(photo)

    async def list_by_user(self, owner_id: int) -> list[Photo]:
        return await self._photo_repo.list_by_user(owner_id)

    def _ensure_owner_or_admin(self, current_user: User, photo: Photo) -> None:
        if current_user.role == UserRole.admin:
            return
        if photo.owner_id != current_user.id:
            raise PermissionDeniedError("Insufficient permissions")
