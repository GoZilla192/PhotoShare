import pytest
from unittest.mock import AsyncMock, MagicMock

from app.repository.token_repository import TokenBlacklistRepository
from app.models.token_blacklist import TokenBlacklist


@pytest.mark.asyncio
async def test_add_token_blacklist_entry():
    # mock session
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    repo = TokenBlacklistRepository(session)

    entry = TokenBlacklist(jti="test-jti")

    result = await repo.add(entry)

    session.add.assert_called_once_with(entry)
    session.flush.assert_awaited_once()
    assert result is entry

@pytest.mark.asyncio
async def test_is_revoked_returns_true():
    session = MagicMock()

    # mock execute
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = 1  # ніби запис існує

    session.execute = AsyncMock(return_value=mock_result)

    repo = TokenBlacklistRepository(session)

    result = await repo.is_revoked("test-jti")

    session.execute.assert_awaited_once()
    assert result is True

@pytest.mark.asyncio
async def test_is_revoked_returns_false():
    session = MagicMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # запису нема

    session.execute = AsyncMock(return_value=mock_result)

    repo = TokenBlacklistRepository(session)

    result = await repo.is_revoked("test-jti")

    session.execute.assert_awaited_once()
    assert result is False