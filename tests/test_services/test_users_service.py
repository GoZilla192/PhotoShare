import pytest
from datetime import datetime, UTC

from app.models.user import User
from app.models.photo import Photo
from app.repository.users_repository import UserRepository
from app.repository.photos_repository import PhotoRepository
from app.service.users_service import UserService
from app.schemas.user_profile_shema import UserMeUpdateRequest
from app.core.exceptions import NotFoundError, PermissionDeniedError, ConflictError
from app.models.roles import UserRole


@pytest.mark.asyncio
async def test_get_public_profile(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    user = User(username="usr1", email="usr1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    profile = await service.get_public_profile_by_username("usr1")

    assert profile.username == "usr1"
    assert profile.photos_count == 0

@pytest.mark.asyncio
async def test_get_public_profile(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    user = User(username="usr1", email="usr1@test.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    profile = await service.get_public_profile_by_username("usr1")

    assert profile.username == "usr1"
    assert profile.photos_count == 0

@pytest.mark.asyncio
async def test_get_public_profile_not_found(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    with pytest.raises(NotFoundError):
        await service.get_public_profile_by_username("unknown")

@pytest.mark.asyncio
async def test_update_me_inactive_user(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    user = User(
        username="usr1",
        email="usr1@test.com",
        password_hash="x",
        is_active=False,
    )

    req = UserMeUpdateRequest(username="new", email=None)

    with pytest.raises(PermissionDeniedError):
        await service.update_me(current_user=user, req=req)

@pytest.mark.asyncio
async def test_update_me_username_conflict(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    usr1 = User(username="usr1", email="usr1@test.com", password_hash="x")
    usr2 = User(username="usr2", email="usr2@test.com", password_hash="x")

    db_session.add_all([usr1, usr2])
    await db_session.flush()

    req = UserMeUpdateRequest(username="usr2", email=None)

    with pytest.raises(ConflictError):
        await service.update_me(current_user=usr1, req=req)

@pytest.mark.asyncio
async def test_ban_user_success(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    admin = User(username="admin", email="a@test.com", password_hash="x", role=UserRole.admin)
    target = User(username="usr1", email="usr1@test.com", password_hash="x")

    db_session.add_all([admin, target])
    await db_session.flush()

    result = await service.ban_user(target_user_id=target.id, current_user=admin)

    assert result.is_active is False

@pytest.mark.asyncio
async def test_update_me_email_conflict(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    usr1 = User(username="usr1", email="usr1@test.com", password_hash="x")
    usr2 = User(username="usr2", email="usr2@test.com", password_hash="x")

    db_session.add_all([usr1, usr2])
    await db_session.flush()

    req = UserMeUpdateRequest(username=None, email="usr2@test.com")

    with pytest.raises(ConflictError):
        await service.update_me(current_user=usr1, req=req)

@pytest.mark.asyncio
async def test_update_me_user_not_found(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    fake_user = User(id=999, username="x", email="x@test.com", password_hash="x")

    req = UserMeUpdateRequest(username="new", email=None)

    with pytest.raises(NotFoundError):
        await service.update_me(current_user=fake_user, req=req)

@pytest.mark.asyncio
async def test_update_me_user_not_found(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    fake_user = User(
        id=999,
        username="x",
        email="x@test.com",
        password_hash="x",
        is_active=True,
    )

    req = UserMeUpdateRequest(username="new", email=None)

    with pytest.raises(NotFoundError):
        await service.update_me(current_user=fake_user, req=req)

@pytest.mark.asyncio
async def test_simple_save(db_session):
    user = User(
        username="test",
        email="t@t.com",
        password_hash="x",
        role=UserRole.user,
    )

    db_session.add(user)
    await db_session.flush()

    assert user.id is not None

    user.role = UserRole.moderator
    await db_session.commit()

    await db_session.refresh(user)

    assert user.role == UserRole.moderator

@pytest.mark.asyncio
async def test_unban_user_success(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    admin = User(username="admin", email="a@test.com", password_hash="x", role=UserRole.admin)
    target = User(username="usr1", email="usr1@test.com", password_hash="x", is_active=False)

    db_session.add_all([admin, target])
    await db_session.flush()

    result = await service.unban_user(target_user_id=target.id, current_user=admin)

    assert result.is_active is True

@pytest.mark.asyncio
async def test_list_users_requires_admin(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    user = User(username="usr1", email="usr1@test.com", password_hash="x", role=UserRole.user)

    with pytest.raises(PermissionDeniedError):
        await service.list_users(limit=10, offset=0, current_user=user)

@pytest.mark.asyncio
async def test_get_public_profile_with_photos_repo(db_session):
    users_repo = UserRepository(db_session)
    photos_repo = PhotoRepository(db_session)

    service = UserService(
        session=db_session,
        users_repo=users_repo,
        photos_repo=photos_repo,
    )

    user = User(username="u1", email="u1@test.com", password_hash="x", is_active=True)
    db_session.add(user)
    await db_session.flush()

    db_session.add(
        Photo(
            user_id=user.id,
            photo_unique_url="p1",
            cloudinary_public_id="dummy",
            description="Test",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    await db_session.flush()

    profile = await service.get_public_profile_by_username("u1")

    assert profile.photos_count == 1

@pytest.mark.asyncio
async def test_ban_user_target_not_found(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    admin = User(
        username="admin",
        email="a@test.com",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
    )

    with pytest.raises(NotFoundError):
        await service.ban_user(target_user_id=999, current_user=admin)

@pytest.mark.asyncio
async def test_set_role_target_not_found(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    admin = User(
        username="admin",
        email="a@test.com",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
    )

    with pytest.raises(NotFoundError):
        await service.set_role(
            target_user_id=999,
            role=UserRole.moderator,
            current_user=admin,
        )

@pytest.mark.asyncio
async def test_unban_user_requires_admin(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    user = User(
        username="u1",
        email="u1@test.com",
        password_hash="x",
        role=UserRole.user,
        is_active=True,
    )

    with pytest.raises(PermissionDeniedError):
        await service.unban_user(target_user_id=1, current_user=user)

@pytest.mark.asyncio
async def test_list_users_success(db_session):
    users_repo = UserRepository(db_session)
    service = UserService(session=db_session, users_repo=users_repo)

    admin = User(
        username="admin",
        email="a@test.com",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
    )

    db_session.add(admin)
    await db_session.flush()

    users = await service.list_users(limit=10, offset=0, current_user=admin)

    assert isinstance(users, list)