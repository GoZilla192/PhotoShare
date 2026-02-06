from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from PhotoShare.app.schemas.rating_schema import RatingCreate, RatingStats
from app.service.rating_service import RatingService
from app.models.user import User
from app.dependency.auth import get_current_user


router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"]
)

@router.post(
    "/photos/{photo_id}",
    status_code=status.HTTP_201_CREATED
)
async def add_rating(
    photo_id: int,
    payload: RatingCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RatingService(session)

    rating = await service.add_rating(
        photo_id=photo_id,
        value=payload.value,
        current_user=current_user
    )

    return {
        "id": rating.id,
        "photo_id": rating.photo_id,
        "user_id": rating.user_id,
        "value": rating.value
    }

@router.get(
    "/photos/{photo_id}",
    response_model=RatingStats
)
async def get_rating_stats(
    photo_id: int,
    session: AsyncSession = Depends(get_db)
):
    service = RatingService(session)
    return await service.get_rating_stats(photo_id)

@router.delete(
    "/{rating_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_rating(
    rating_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = RatingService(session)
    await service.delete_rating(
        rating_id=rating_id,
        current_user=current_user
    )