from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user, require_admin
from app.dependency.dependencies import user_service as get_user_service
from app.models import UserRole
from app.service.users_service import UserService
from app.schemas.user_profile_shema import (
    UserPublicProfile,
    UserMeProfile,
    UserMeUpdateRequest,
    UserBanResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserMeProfile)
async def get_me(
    current_user=Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    """
    Returns current user's profile (editable view).
    """
    return await svc.get_me(current_user)


@router.patch("/me", response_model=UserMeProfile)
async def update_me(
    body: UserMeUpdateRequest,
    current_user=Depends(get_current_user),
    svc: UserService = Depends(get_user_service),
):
    """
    Updates current user's editable profile fields (username/bio/avatar_url etc).
    """
    return await svc.update_me(current_user=current_user, req=body)


@router.get("/{username}", response_model=UserPublicProfile)
async def get_public_profile(
    username: str,
    svc: UserService = Depends(get_user_service),
):
    """
    Public profile by unique username.
    """
    return await svc.get_public_profile_by_username(username)


@router.patch("/{user_id}/ban", response_model=UserBanResponse)
async def ban_user(
    user_id: int,
    admin_user = Depends(require_admin),
    svc: UserService = Depends(get_user_service),
):
    """
    Admin action: set user inactive (ban).
    """
    return await svc.ban_user(target_user_id=user_id, current_user=admin_user)


@router.patch("/{user_id}/unban", response_model=UserBanResponse)
async def unban_user(
    user_id: int,
    admin_user = Depends(require_admin),
    svc: UserService = Depends(get_user_service),
):
    """
    Admin action: set user active (unban).
    """
    return await svc.unban_user(target_user_id=user_id, current_user=admin_user)


@router.patch("/{user_id}/role", status_code=status.HTTP_204_NO_CONTENT)
async def set_role(
    user_id: int,
    role: UserRole,
    admin_user=Depends(require_admin),
    svc: UserService = Depends(get_user_service),
):
    await svc.set_role(target_user_id=user_id, role=role, current_user=admin_user)
    return None

