from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_token
from app.core.settings import Settings
from fastapi.templating import Jinja2Templates
from app.dependency.dependencies import get_session, get_settings
from app.repository.token_repository import TokenBlacklistRepository
from app.repository.users_repository import UserRepository


COOKIE_NAME = "access_token"

def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


async def get_current_user_ui(
    access_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(token=access_token, settings=settings)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise HTTPException(status_code=401, detail="Invalid token")

    if await TokenBlacklistRepository(session).is_revoked(jti):
        raise HTTPException(status_code=401, detail="Token revoked")

    user = await UserRepository(session).get_by_id(int(sub))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or not found")

    return user

def get_token_from_cookie(access_token: str | None = Cookie(default=None, alias=COOKIE_NAME)) -> str | None:
    return access_token

def require_roles_ui(*roles: str):
    async def dep(user=Depends(get_current_user_ui)):
        user_role = getattr(user.role, "value", user.role)
        if user_role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dep

async def require_admin_ui(user=Depends(get_current_user_ui)):
    user_role = getattr(user.role, "value", user.role)
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user