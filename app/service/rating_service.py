from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rating import Rating
from app.repository.ratings_repository import RatingRepository
from app.repository.photos_repository import PhotoRepository


class RatingService:
    def __init__(
        self,
        session: AsyncSession,
        ratings_repo: RatingRepository,
        photos_repo: PhotoRepository,
    ):
        self.session = session
        self.rating_repo = ratings_repo
        self.photo_repo = photos_repo

    async def add_rating(
        self,
        photo_id: int,
        user_id: int,
        value: int,
    ) -> Rating:
        """
        Adds a rating to a photo.

        Rules:
        - photo must exist
        - user cannot rate own photo
        - user can only rate once
        """

        # Checking the existence of a photo
        photo = await self.photo_repo.get_by_id(photo_id)
        if photo is None:
            raise ValueError("Photo not found")

        # Prohibition of rating your own photo
        if photo.user_id == user_id:
            raise PermissionError("You cannot rate your own photo")

        # Re-voting verification
        existing = await self.rating_repo.get_by_photo_and_user(
            photo_id=photo_id,
            user_id=user_id,
        )
        if existing:
            raise PermissionError("You have already rated this photo")

        rating = Rating(
            photo_id=photo_id,
            user_id=user_id,
            value=value,
        )

        try:
            return await self.rating_repo.create(rating)

        except IntegrityError:
            # Race condition protection
            await self.session.rollback()
            raise PermissionError("You have already rated this photo")

    async def get_rating_stats(self, photo_id: int) -> dict:
        """
        Returns the average value and number of ratings.
        """

        photo = await self.photo_repo.get_by_id(photo_id)
        if photo is None:
            raise ValueError("Photo not found")

        return await self.rating_repo.get_rating_stats(photo_id)

    async def delete_rating(
        self,
        rating_id: int,
        actor_role: str,
    ) -> None:
        """
        Deleting the rating.

        Access:
        - moderator
        - admin
        """

        if actor_role not in ("moderator", "admin"):
            raise PermissionError("Not enough permissions")

        rating = await self.rating_repo.get_by_id(rating_id)
        if rating is None:
            raise ValueError("Rating not found")

        await self.rating_repo.delete(rating)