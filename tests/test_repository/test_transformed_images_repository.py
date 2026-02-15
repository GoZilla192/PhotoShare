import pytest

from datetime import datetime, UTC
from app.repository.transformed_images_repository import TransformedImageRepository
from app.models.transformed_image import TransformedImage
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.photo_tags import PhotoTag


@pytest.mark.asyncio
async def test_add_transformed_image(db_session):
    repo = TransformedImageRepository(db_session)

    obj = TransformedImage(
        photo_id=1,
        image_url="url1",
        transformation="resize",
    )

    created = await repo.add(obj)

    assert created.id is not None

@pytest.mark.asyncio
async def test_create_for_photo(db_session):
    repo = TransformedImageRepository(db_session)

    created = await repo.create_for_photo(
        photo_id=1,
        image_url="url2",
        transformation=None,
    )

    assert created.id is not None
    assert created.transformation is None

@pytest.mark.asyncio
async def test_create_for_photo(db_session):
    repo = TransformedImageRepository(db_session)

    created = await repo.create_for_photo(
        photo_id=1,
        image_url="url2",
        transformation=None,
    )

    assert created.id is not None
    assert created.transformation is None

@pytest.mark.asyncio
async def test_get_transformed_image_by_id(db_session):
    repo = TransformedImageRepository(db_session)

    obj = TransformedImage(
        photo_id=1,
        image_url="url3",
        transformation="crop",
    )

    db_session.add(obj)
    await db_session.flush()

    found = await repo.get_by_id(obj.id)
    assert found is not None

    missing = await repo.get_by_id(999)
    assert missing is None

@pytest.mark.asyncio
async def test_list_for_photo(db_session):
    repo = TransformedImageRepository(db_session)

    photo_id = 1

    for i in range(5):
        db_session.add(
            TransformedImage(
                photo_id=photo_id,
                image_url=f"url{i}",
                transformation="resize",
            )
        )

    db_session.add(
        TransformedImage(
            photo_id=2,
            image_url="other",
            transformation="resize",
        )
    )

    await db_session.flush()

    images = await repo.list_for_photo(photo_id=1, limit=10, offset=0)
    assert len(images) == 5

    limited = await repo.list_for_photo(photo_id=1, limit=2, offset=0)
    assert len(limited) == 2

    offset = await repo.list_for_photo(photo_id=1, limit=10, offset=2)
    assert len(offset) == 3