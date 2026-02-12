import pytest
from app.models.photo import Photo
from app.core.exceptions import NotFoundError


@pytest.mark.asyncio
async def test_get_photo_by_unique_url_integration(db_session, photo_service_factory):
    service = photo_service_factory()

    photo = Photo(
        user_id=1,
        photo_unique_url="integration-test-url",
        cloudinary_public_id="dummy",
        description="integration test",
    )

    async with db_session.begin():
        await service.photos.add(photo)

    result = await service.get_photo_by_unique_url("integration-test-url")

    assert result.id is not None

@pytest.mark.asyncio
async def test_get_photo_by_unique_url_not_found_integration(photo_service_factory):
    service = photo_service_factory()

    with pytest.raises(NotFoundError):
        await service.get_photo_by_unique_url("missing-url")