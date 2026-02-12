import pytest

from app.service.photos_service import PhotoService
from app.models.photo import Photo
from app.core.exceptions import NotFoundError


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