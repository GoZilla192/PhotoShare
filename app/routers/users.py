from fastapi import APIRouter, HTTPException, status

from app.schemas.user_profile_shema import (
    UserPublicProfile,
    UserMeProfile,
    UserMeUpdateRequest,
    UserBanResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMeProfile)
async def get_me():
    """
    Returns current user's profile (editable view). (stub)
    TODO: require auth, return email/is_active, photos_count.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.patch("/me", response_model=UserMeProfile)
async def update_me(body: UserMeUpdateRequest):
    """
    Updates current user's editable profile fields. (stub)
    TODO: require auth, update allowed fields only.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{username}", response_model=UserPublicProfile)
async def get_public_profile(username: str):
    """
    Public profile by unique username. (stub)
    TODO: return created_at, photos_count, etc.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.patch("/{user_id}/ban", response_model=UserBanResponse)
async def ban_user(user_id: int):
    """
    Admin action: set user inactive (ban). (stub)
    TODO: require admin role; set is_active=False.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
