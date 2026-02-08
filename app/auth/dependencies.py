from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_token
from app.dependency.dependencies import get_session, get_settings
from app.repository.token_repository import TokenBlacklistRepository
from app.repository.users_repository import UserRepository
from app.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # поправ під твій роут

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    try:
        payload = decode_token(token=token, settings=settings)
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


def require_roles(*roles: str):
    async def dep(user=Depends(get_current_user)):
        user_role = getattr(user.role, "value", user.role)
        if user_role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dep

def require_admin(user=Depends(get_current_user)):
    user_role = getattr(user.role, "value", user.role)
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user