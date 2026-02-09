from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user, oauth2_scheme
from app.auth.service import AuthService
from app.dependency.dependencies import auth_service as get_auth_service, auth_service
from app.models import User

from app.schemas.auth_schema import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: RegisterRequest,
    auth: AuthService = Depends(get_auth_service),
):
    """
    Register new user.
    - First user may become admin (handled in AuthService).
    - Returns access_token.
    """
    token = await auth.register(**data.model_dump())
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login")
async def login_user(
    data: LoginRequest,
    auth: AuthService = Depends(get_auth_service),
):
    """
    Login user and return access_token.
    AuthService handles password validation, inactive user, etc.
    """
    token = await auth.login(**data.model_dump())
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
        current_user: User = Depends(get_current_user),
        token: str = Depends(oauth2_scheme),  # <- беремо поточний bearer токен
        auth: AuthService = Depends(auth_service),
):
    """
    Logout = blacklist current token JTI until exp.
    Requires Authorization: Bearer <token>.
    """
    await auth.logout(token)
    return

