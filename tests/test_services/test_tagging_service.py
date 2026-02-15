import pytest
from datetime import datetime, UTC

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.photo import Photo
from app.models.user import User
from app.models.roles import UserRole
from app.repository.photos_repository import PhotoRepository
from app.repository.tags_repository import TagRepository
from app.service.tagging_service import TaggingService


@pytest.mark.asyncio
async def test_get_photo_tags_not_found(db_session):
    service = TaggingService(
        session=db_session,
        tags_repo=TagRepository(db_session),
        photos_repo=PhotoRepository(db_session),
    )

    with pytest.raises(NotFoundError):
        await service.get_photo_tags(photo_id=999)

@pytest.mark.asyncio
async def test_get_photo_tags_success(db_session):
    tags_repo = TagRepository(db_session)
    photos_repo = PhotoRepository(db_session)

    service = TaggingService(db_session, tags_repo, photos_repo)

    photo = Photo(
        user_id=1,
        photo_unique_url="p1",
        cloudinary_public_id="x",
        description="test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    await tags_repo.set_tags_for_photo(photo.id, ["a", "b"])

    result = await service.get_photo_tags(photo_id=photo.id)

    assert sorted(result) == ["a", "b"]

@pytest.mark.asyncio
async def test_set_photo_tags_not_found(db_session):
    service = TaggingService(
        db_session,
        TagRepository(db_session),
        PhotoRepository(db_session),
    )

    user = User(id=1, role=UserRole.user)

    with pytest.raises(NotFoundError):
        await service.set_photo_tags(
            photo_id=999,
            tag_names=["a"],
            current_user=user,
        )

@pytest.mark.asyncio
async def test_set_photo_tags_not_owner(db_session):
    tags_repo = TagRepository(db_session)
    photos_repo = PhotoRepository(db_session)

    service = TaggingService(db_session, tags_repo, photos_repo)

    photo = Photo(
        user_id=1,
        photo_unique_url="p2",
        cloudinary_public_id="x",
        description="test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    user = User(id=2, role=UserRole.user)

    with pytest.raises(PermissionDeniedError):
        await service.set_photo_tags(
            photo_id=photo.id,
            tag_names=["a"],
            current_user=user,
        )

@pytest.mark.asyncio
async def test_set_photo_tags_owner_success(db_session):
    tags_repo = TagRepository(db_session)
    photos_repo = PhotoRepository(db_session)

    service = TaggingService(db_session, tags_repo, photos_repo)

    photo = Photo(
        user_id=1,
        photo_unique_url="p3",
        cloudinary_public_id="x",
        description="test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    user = User(id=1, role=UserRole.user)

    result = await service.set_photo_tags(
        photo_id=photo.id,
        tag_names=["a", "b"],
        current_user=user,
    )

    assert sorted(result) == ["a", "b"]

@pytest.mark.asyncio
async def test_set_photo_tags_admin_success(db_session):
    tags_repo = TagRepository(db_session)
    photos_repo = PhotoRepository(db_session)

    service = TaggingService(db_session, tags_repo, photos_repo)

    photo = Photo(
        user_id=1,
        photo_unique_url="p4",
        cloudinary_public_id="x",
        description="test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    admin = User(id=999, role=UserRole.admin)

    result = await service.set_photo_tags(
        photo_id=photo.id,
        tag_names=["admin"],
        current_user=admin,
    )

    assert result == ["admin"]

def test_parse_tags_csv_none():
    service = TaggingService(None, None, None)
    assert service._parse_tags_csv(None) is None

def test_parse_tags_csv_empty():
    service = TaggingService(None, None, None)
    assert service._parse_tags_csv("") is None

def test_parse_tags_csv_trim_and_limit():
    service = TaggingService(None, None, None)

    result = service._parse_tags_csv(" a, b , ,c,d,e,f ")

    assert result == ["a", "b", "c", "d", "e"]  # clamp to 5

@pytest.mark.asyncio
async def test_get_tag_cloud(db_session):
    tags_repo = TagRepository(db_session)
    photos_repo = PhotoRepository(db_session)

    service = TaggingService(db_session, tags_repo, photos_repo)

    photo = Photo(
        user_id=1,
        photo_unique_url="p5",
        cloudinary_public_id="x",
        description="test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    await tags_repo.set_tags_for_photo(photo.id, ["a", "a", "b"])

    cloud = await service.get_tag_cloud()

    assert isinstance(cloud, list)
    assert "name" in cloud[0]
    assert "count" in cloud[0]