from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.dependency.dependencies import rating_service
from app.schemas.rating_schema import (
    RatingSetRequest,
    RatingResponse
)
from app.service.rating_service import RatingService


router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.get(
    "/photos/{photo_id}",
    response_model=RatingResponse
)
async def get_rating_stats(
    photo_id: int,
    svc: RatingService = Depends(rating_service),
):
    return await svc.get_rating_stats(photo_id)


@router.post(
    "/photos/{photo_id}",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rating(
    photo_id: int,
    body: RatingSetRequest,
    current_user=Depends(get_current_user),
    svc: RatingService = Depends(rating_service),
):
    try:
        await svc.add_rating(
            photo_id=photo_id,
            user_id=current_user.id,
            value=body.value,
        )

        return await svc.get_rating_stats(photo_id)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.delete(
    "/{rating_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_rating(
    rating_id: int,
    current_user=Depends(get_current_user),
    svc: RatingService = Depends(rating_service),
):
    try:
        await svc.delete_rating(
            rating_id=rating_id,
            actor_role=current_user.role,
        )
        return

    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc