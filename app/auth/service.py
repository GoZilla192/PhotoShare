from __future__ import annotations

from datetime import datetime, timezone

from app.auth.security import decode_token, hash_password, create_access_token, verify_password
from app.models import User, UserRole
from app.models.token_blacklist import TokenBlacklist
from app.repository.token_repository import TokenBlacklistRepository
from app.repository.users_repository import UserRepository


class AuthError(Exception): ...
class ConflictError(AuthError): ...
class InvalidCredentialsError(AuthError): ...
class InactiveUserError(AuthError): ...


class AuthService:
    def __init__(self, users: UserRepository, blacklist: TokenBlacklistRepository):
        self.users = users
        self.blacklist = blacklist

    async def register(self, *, username: str, email: str, password: str) -> User:
        if await self.users.get_by_email(email):
            raise ConflictError("Email already registered")
        if await self.users.get_by_username(username):
            raise ConflictError("Username already taken")

        is_first_user = not await self.users.exists_any()
        role = UserRole.admin if is_first_user else UserRole.user

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )

        # repo: add + flush; commit буде зовні
        return await self.users.add(user)

    async def login(self, *, email: str, password: str) -> dict:
        user = await self.users.get_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid credentials")
        if not user.is_active:
            raise InactiveUserError("User inactive")
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        # повертаємо пакет який очікує router/schemas
        token_pack = create_access_token(subject=str(user.id), role=user.role.value)
        return token_pack

    async def logout(self, token: str) -> None:
        # якщо токен невалідний/прострочений — logout no-op
        try:
            payload = decode_token(token)
        except Exception:
            return

        jti = payload.get("jti")
        sub = payload.get("sub")
        exp = payload.get("exp")

        if not jti or not sub or not exp:
            return

        expires_at = datetime.fromtimestamp(int(exp), tz=timezone.utc)
        await self.blacklist.add(
            TokenBlacklist(jti=jti, user_id=int(sub), expires_at=expires_at)
        )