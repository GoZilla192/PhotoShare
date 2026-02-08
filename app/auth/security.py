# app/auth/security.py
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError,  ExpiredSignatureError
from jose.exceptions import JWEInvalidAuth
from passlib.context import CryptContext

from app.settings import Settings  # SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str, *, settings: Settings) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError as e:
        raise ValueError("Token expired") from e
    except JWEInvalidAuth as e:
        raise ValueError("Invalid token") from e
    except JWTError as e:
        raise ValueError("Invalid authentication") from e
