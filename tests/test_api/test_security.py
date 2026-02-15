import pytest
from types import SimpleNamespace
from unittest.mock import patch
from jose.exceptions import JWEInvalidAuth
from fastapi import Request
from starlette.datastructures import Headers

from app.auth.security import create_access_token, decode_token, hash_password, verify_password, extract_token


def test_verify_password_success():
    password = "secret123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True

def test_verify_password_fail():
    password = "secret123"
    hashed = hash_password(password)

    assert verify_password("wrong", hashed) is False

def test_create_and_decode_token_success():
    settings = SimpleNamespace(
        SECRET_KEY="test-secret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
    )

    token = create_access_token(
        user_id=1,
        role="admin",
        settings=settings,
    )

    payload = decode_token(token, settings=settings)

    assert payload["sub"] == "1"
    assert payload["role"] == "admin"
    assert "jti" in payload

from datetime import timedelta
import pytest


def test_decode_token_expired():
    settings = SimpleNamespace(
        SECRET_KEY="test-secret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=-1,  # вже прострочений
    )

    token = create_access_token(
        user_id=1,
        role="admin",
        settings=settings,
    )

    with pytest.raises(ValueError, match="Token expired"):
        decode_token(token, settings=settings)

def test_decode_token_invalid_signature():
    settings = SimpleNamespace(
        SECRET_KEY="test-secret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
    )

    token = create_access_token(
        user_id=1,
        role="admin",
        settings=settings,
    )

    # інший секрет → зламаємо підпис
    wrong_settings = SimpleNamespace(
        SECRET_KEY="wrong-secret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
    )

    with pytest.raises(ValueError, match="Invalid authentication"):
        decode_token(token, settings=wrong_settings)

def test_decode_token_invalid_token():
    settings = SimpleNamespace(
        SECRET_KEY="test-secret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
    )

    with patch("app.auth.security.jwt.decode", side_effect=JWEInvalidAuth()):
        with pytest.raises(ValueError, match="Invalid token"):
            decode_token("fake", settings=settings)

def test_extract_token_from_header():
    scope = {
        "type": "http",
        "headers": [(b"authorization", b"Bearer testtoken")],
    }
    request = Request(scope)

    token = extract_token(request)

    assert token == "testtoken"

from unittest.mock import patch, MagicMock

def test_extract_token_none():
    scope = {"type": "http", "headers": []}
    request = Request(scope)

    with patch("app.auth.security.settings", new=MagicMock(COOKIE_NAME="access_token")):
        token = extract_token(request)

    assert token is None