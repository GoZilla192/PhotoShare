from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.rating import Rating
from app.repository.ratings_repository import RatingRepository
from app.repository.photos_repository import PhotoRepository
from app.models.user import User


class RatingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.rating_repo = RatingRepository(session)
        self.photo_repo = PhotoRepository(session)

    # CREATE
    async def add_rating(
        self,
        photo_id: int,
        value: int,
        current_user: User
    ) -> Rating:
        """
        Adds a rating to a photo.

        Checks:
        1. Photo exists
        2. User is not the owner of the photo
        3. User has not voted yet
        4. Rating value is valid (1..5) — we assume that
        Pydantic has already done this
        """

        # check if photo exist
        photo = await self.photo_repo.get_by_id(photo_id)
        if photo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )

        # user can't rate own photo
        if photo.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot rate your own photo"
            )

        # if photo already rated by this user
        existing_rating = await self.rating_repo.get_by_photo_and_user(
            photo_id=photo_id,
            user_id=current_user.id
        )
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already rated this photo"
            )

        # create rating
        rating = Rating(
            photo_id=photo_id,
            user_id=current_user.id,
            value=value
        )

        try:
            return await self.rating_repo.create(rating)

        except IntegrityError:
            # Race condition protection:
            # two requests at the same time -> UNIQUE(photo_id, user_id)
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already rated this photo"
            )

    # READ (stats)
    async def get_rating_stats(self, photo_id: int) -> dict:
        """
        Returns the average rating and number of ratings.
        """

        photo = await self.photo_repo.get_by_id(photo_id)
        if photo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )

        return await self.rating_repo.get_rating_stats(photo_id)

    # DELETE (moderator / admin)
    async def delete_rating(
        self,
        rating_id: int,
        current_user: User
    ) -> None:
        """
        Removing rating.
        Access: moderator, admin
        """

        # role check
        if current_user.role not in ("moderator", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        # rating search
        rating = await self.rating_repo.get_by_id(rating_id)
        if rating is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found"
            )

        # delete
        await self.rating_repo.delete(rating)