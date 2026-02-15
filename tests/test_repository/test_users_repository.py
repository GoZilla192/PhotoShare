import pytest

from app.repository.users_repository import UserRepository
from app.models.user import User


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    repo = UserRepository(db_session)

    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    result = await repo.get_by_id(user.id)
    assert result is not None
    assert result.username == "u1"

    missing = await repo.get_by_id(999)
    assert missing is None

@pytest.mark.asyncio
async def test_get_first_user_id(db_session):
    repo = UserRepository(db_session)

    assert await repo.get_first_user_id() is None

    db_session.add_all([
        User(username="u2", email="u2@test.com", password_hash="x"),
        User(username="u1", email="u1@test.com", password_hash="x"),
    ])
    await db_session.flush()

    first_id = await repo.get_first_user_id()
    assert first_id is not None

@pytest.mark.asyncio
async def test_get_by_username_and_email(db_session):
    repo = UserRepository(db_session)

    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    assert await repo.get_by_username("u1") is not None
    assert await repo.get_by_username("unknown") is None

    assert await repo.get_by_email("u1@test.com") is not None
    assert await repo.get_by_email("no@test.com") is None

@pytest.mark.asyncio
async def test_add_user(db_session):
    repo = UserRepository(db_session)

    user = User(username="new", email="new@test.com", password_hash="x")
    result = await repo.add(user)

    assert result.id is not None

@pytest.mark.asyncio
async def test_update_profile_fields(db_session):
    repo = UserRepository(db_session)

    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    updated = await repo.update_profile_fields(
        user.id,
        username="newname"
    )

    assert updated.username == "newname"

    # без змін — повертає існуючого
    same = await repo.update_profile_fields(user.id)
    assert same.id == user.id

    # неіснуючий
    missing = await repo.update_profile_fields(999, username="x")
    assert missing is None

@pytest.mark.asyncio
async def test_set_is_active(db_session):
    repo = UserRepository(db_session)

    user = User(username="u1", email="u1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    result = await repo.set_is_active(user.id, False)
    assert result is True

    missing = await repo.set_is_active(999, True)
    assert missing is False

@pytest.mark.asyncio
async def test_exists_any(db_session):
    repo = UserRepository(db_session)

    assert await repo.exists_any() is False

    db_session.add(User(username="u1", email="u1@test.com", password_hash="x"))
    await db_session.flush()

    assert await repo.exists_any() is True

@pytest.mark.asyncio
async def test_list_users(db_session):
    repo = UserRepository(db_session)

    for i in range(5):
        db_session.add(
            User(username=f"u{i}", email=f"u{i}@test.com", password_hash="x")
        )

    await db_session.flush()

    users = await repo.list_users(limit=10, offset=0)
    assert len(users) == 5

    limited = await repo.list_users(limit=2, offset=0)
    assert len(limited) == 2

    offset = await repo.list_users(limit=10, offset=2)
    assert len(offset) == 3