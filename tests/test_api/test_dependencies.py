import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.auth.dependencies import get_current_user
from app.auth.dependencies import require_roles
from app.auth.dependencies import require_admin


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with patch("app.auth.dependencies.decode_token", side_effect=ValueError):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(
                token="bad",
                session=AsyncMock(),
                settings=MagicMock(),
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid token"

@pytest.mark.asyncio
async def test_get_current_user_missing_jti_or_sub():
    with patch("app.auth.dependencies.decode_token", return_value={}):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(
                token="token",
                session=AsyncMock(),
                settings=MagicMock(),
            )

        assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_revoked_token():
    session = AsyncMock()

    with patch("app.auth.dependencies.decode_token",
               return_value={"jti": "123", "sub": "1"}):
        with patch("app.auth.dependencies.TokenBlacklistRepository") as mock_repo:

            mock_repo.return_value.is_revoked = AsyncMock(return_value=True)

            with pytest.raises(HTTPException) as exc:
                await get_current_user(
                    token="token",
                    session=session,
                    settings=MagicMock(),
                )

            assert exc.value.status_code == 401
            assert exc.value.detail == "Token revoked"

@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    session = AsyncMock()

    with patch("app.auth.dependencies.decode_token",
               return_value={"jti": "123", "sub": "1"}):
        with patch("app.auth.dependencies.TokenBlacklistRepository") as mock_blacklist:
            mock_blacklist.return_value.is_revoked = AsyncMock(return_value=False)

            with patch("app.auth.dependencies.UserRepository") as mock_user_repo:
                mock_user_repo.return_value.get_by_id = AsyncMock(return_value=None)

                with pytest.raises(HTTPException) as exc:
                    await get_current_user(
                        token="token",
                        session=session,
                        settings=MagicMock(),
                    )

                assert exc.value.status_code == 401
                assert exc.value.detail == "User inactive or not found"

@pytest.mark.asyncio
async def test_get_current_user_success():
    session = AsyncMock()
    fake_user = MagicMock()
    fake_user.is_active = True

    with patch("app.auth.dependencies.decode_token",
               return_value={"jti": "123", "sub": "1"}):
        with patch("app.auth.dependencies.TokenBlacklistRepository") as mock_blacklist:
            mock_blacklist.return_value.is_revoked = AsyncMock(return_value=False)

            with patch("app.auth.dependencies.UserRepository") as mock_user_repo:
                mock_user_repo.return_value.get_by_id = AsyncMock(return_value=fake_user)

                result = await get_current_user(
                    token="token",
                    session=session,
                    settings=MagicMock(),
                )

                assert result is fake_user

@pytest.mark.asyncio
async def test_require_roles_forbidden():
    dep = require_roles("admin")

    fake_user = MagicMock()
    fake_user.role = "user"

    with pytest.raises(HTTPException) as exc:
        await dep(user=fake_user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Insufficient role"

@pytest.mark.asyncio
async def test_require_roles_success():
    dep = require_roles("admin", "moderator")

    fake_user = MagicMock()
    fake_user.role = "admin"

    result = await dep(user=fake_user)

    assert result is fake_user

def test_require_admin_forbidden():
    fake_user = MagicMock()
    fake_user.role = "user"

    with pytest.raises(HTTPException) as exc:
        require_admin(user=fake_user)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Admin only"

def test_require_admin_success():
    fake_user = MagicMock()
    fake_user.role = "admin"

    result = require_admin(user=fake_user)

    assert result is fake_user