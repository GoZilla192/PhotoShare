import pytest
from unittest.mock import Mock, AsyncMock

from app.service.photos_service import PhotoService
from app.models.photo import Photo
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.user import User
from app.models.roles import UserRole
from app.repository.photos_repository import PhotoRepository


class FakePhotoRepository:
    def __init__(self, photo=None):
        self._photo = photo

    async def get_by_unique_url(self, unique_url: str):
        return self._photo


@pytest.mark.asyncio
async def test_get_photo_by_unique_url_raises_if_not_found(db_session):
    service = PhotoService(
        session=db_session,
        photos_repo=FakePhotoRepository(photo=None),
        cloudinary_client=None,
        tags_repo=None,
    )

    with pytest.raises(NotFoundError):
        await service.get_photo_by_unique_url("non-existent-url")


@pytest.mark.asyncio
async def test_get_photo_by_unique_url_returns_photo(db_session):
    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="abc123",
    )

    service = PhotoService(
        session=db_session,
        photos_repo=FakePhotoRepository(photo=photo),
        cloudinary_client=None,
        tags_repo=None,
    )

    result = await service.get_photo_by_unique_url("abc123")

    assert result is photo

def test_ensure_owner_or_admin():
    service = PhotoService(
        session=None,
        photos_repo=None,
        cloudinary_client=None,
        tags_repo=None,
    )

    owner = User(id=1, role=UserRole.user)
    admin = User(id=2, role=UserRole.admin)

    # admin — ok
    service.ensure_owner_or_admin(admin, photo_user_id=1)

    # owner — ok
    service.ensure_owner_or_admin(owner, photo_user_id=1)

    # чужий user — error
    other = User(id=3, role=UserRole.user)
    with pytest.raises(PermissionDeniedError):
        service.ensure_owner_or_admin(other, photo_user_id=1)

@pytest.mark.asyncio
async def test_update_description_permission_denied(db_session):
    repo = PhotoRepository(db_session)
    service = PhotoService(
        session=db_session,
        photos_repo=repo,
        cloudinary_client=Mock(),
        tags_repo=Mock(),
    )

    photo = Photo(user_id=1, photo_unique_url="x", cloudinary_public_id="id")
    db_session.add(photo)
    await db_session.flush()

    other_user = User(id=2, role=UserRole.user)

    with pytest.raises(PermissionDeniedError):
        await service.update_description(photo.id, "new", other_user)

@pytest.mark.asyncio
async def test_create_photo_cleanup_on_error(db_session):
    photos_repo = Mock()
    photos_repo.add.side_effect = Exception("DB error")

    cloudinary = Mock()
    cloudinary.upload_photo.return_value = {"public_id": "pid"}

    service = PhotoService(
        session=db_session,
        photos_repo=photos_repo,
        cloudinary_client=cloudinary,
        tags_repo=Mock(),
    )

    with pytest.raises(Exception):
        await service.create_photo(
            user_id=1,
            file=b"x",
            photo_unique_url="u",
            description=None,
            tags=None,
        )

    cloudinary.delete_photo.assert_called_once_with("pid")

@pytest.mark.asyncio
async def test_search_photos_calls_repo():
    photos_repo = Mock()
    photos_repo.search = AsyncMock(return_value=["item"])
    photos_repo.count_search = AsyncMock(return_value=5)

    service = PhotoService(
        session=Mock(),
        photos_repo=photos_repo,
        cloudinary_client=Mock(),
        tags_repo=Mock(),
    )

    items, total = await service.search_photos(q="x")

    assert items == ["item"]
    assert total == 5

class DummyTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

class DummySession:
    def begin(self):
        return DummyTransaction()

@pytest.mark.asyncio
async def test_delete_photo_cloudinary_cleanup():
    photos_repo = Mock()
    photos_repo.get_by_id = AsyncMock(
        return_value=Photo(
            id=1,
            user_id=1,
            cloudinary_public_id="pid",
        )
    )
    photos_repo.delete_by_id = AsyncMock(return_value=True)

    cloudinary = Mock()
    cloudinary.delete_photo.side_effect = Exception("fail")

    service = PhotoService(
        session=DummySession(),
        photos_repo=photos_repo,
        cloudinary_client=cloudinary,
        tags_repo=Mock(),
    )

    owner = User(id=1, role=UserRole.user)

    await service.delete_photo(1, owner)

    cloudinary.delete_photo.assert_called_once()