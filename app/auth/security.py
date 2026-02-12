from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError,  ExpiredSignatureError
from jose.exceptions import JWEInvalidAuth
from passlib.context import CryptContext
from fastapi import Request

from app.core import settings
from app.core.settings import Settings  # SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(*, user_id: int, role: str, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str, *, settings: Settings) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError as e:
        raise ValueError("Token expired") from e
    except JWEInvalidAuth as e:
        raise ValueError("Invalid token") from e
    except JWTError as e:
        raise ValueError("Invalid authentication") from e

def extract_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()

    token = request.cookies.get(settings.COOKIE_NAME)
    return token