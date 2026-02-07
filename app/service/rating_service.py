from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundError, PermissionDeniedError
from app.models import UserRole
from app.repository.ratings_repository import RatingRepository
from app.repository.photos_repository import PhotoRepository
from app.models.user import User


class RatingService:
    def __init__(self, session: AsyncSession,
                 ratings_repo: RatingRepository,
                 photos_repo: PhotoRepository):
        self.session = session
        self.ratings = ratings_repo
        self.photos = photos_repo

    async def set_rating(self, *, photo_id: int, value: int, current_user: User):
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")
        if photo.user_id == current_user.id:
            raise PermissionDeniedError("You cannot rate your own photo")

        async with self.session.begin():
            await self.ratings.upsert(photo_id=photo_id, user_id=current_user.id, rating=value)

    async def get_stats(self, *, photo_id: int) -> dict:
        photo = await self.photos.get_by_id(photo_id)
        if not photo:
            raise NotFoundError("Photo not found")
        avg, cnt = await self.ratings.get_aggregate(photo_id)
        return {"avg": avg, "count": cnt}

    async def delete_rating_as_moderator(self, *, photo_id: int, user_id: int, current_user: User) -> None:
        if current_user.role not in {UserRole.admin, UserRole.moderator}:
            raise PermissionDeniedError("Not enough permissions")
        async with self.session.begin():
            await self.ratings.delete_for_user(photo_id=photo_id, user_id=user_id)