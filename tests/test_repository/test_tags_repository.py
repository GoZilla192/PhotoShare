import pytest

from datetime import datetime, UTC
from app.repository.tags_repository import TagRepository
from app.models.photo import Photo
from app.models.tag import Tag


@pytest.mark.asyncio
async def test_list_all_tags(db_session):
    repo = TagRepository(db_session)

    db_session.add_all([
        Tag(name="b"),
        Tag(name="a"),
        Tag(name="c"),
    ])
    await db_session.flush()

    tags = await repo.list_all(limit=10, offset=0)

    assert [t.name for t in tags] == ["a", "b", "c"]

    limited = await repo.list_all(limit=2, offset=0)
    assert len(limited) == 2

    offset = await repo.list_all(limit=10, offset=1)
    assert [t.name for t in offset] == ["b", "c"]

@pytest.mark.asyncio
async def test_get_by_names_normalization(db_session):
    repo = TagRepository(db_session)

    db_session.add(Tag(name="nature"))
    await db_session.flush()

    tags = await repo.get_by_names([" Nature ", "nature", "", None])

    assert len(tags) == 1
    assert tags[0].name == "nature"

@pytest.mark.asyncio
async def test_get_or_create_by_names(db_session):
    repo = TagRepository(db_session)

    tags = await repo.get_or_create_by_names(["Test", "Example"])

    assert len(tags) == 2

    names = sorted([t.name for t in tags])
    assert names == ["example", "test"]

    # повторний виклик не створює дублікати
    again = await repo.get_or_create_by_names(["test"])
    assert len(again) == 1

@pytest.mark.asyncio
async def test_set_tags_for_photo(db_session):
    repo = TagRepository(db_session)

    photo = Photo(
        user_id=1,
        photo_unique_url="photo-tags",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    attached = await repo.set_tags_for_photo(
        photo_id=photo.id,
        tag_names=["Nature", "Sunset", "Nature"],
        max_tags=5,
    )

    assert sorted(attached) == ["nature", "sunset"]

    # перезапис
    attached2 = await repo.set_tags_for_photo(
        photo_id=photo.id,
        tag_names=["Ocean"],
    )

    assert attached2 == ["ocean"]

@pytest.mark.asyncio
async def test_list_tag_names_for_photo(db_session):
    repo = TagRepository(db_session)

    photo = Photo(
        user_id=1,
        photo_unique_url="photo-list",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    await repo.set_tags_for_photo(photo.id, ["b", "a"])

    names = await repo.list_tag_names_for_photo(photo.id)

    assert names == ["a", "b"]  # сортовані

@pytest.mark.asyncio
async def test_list_cloud(db_session):
    repo = TagRepository(db_session)

    photo1 = Photo(
        user_id=1,
        photo_unique_url="cloud1",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    photo2 = Photo(
        user_id=1,
        photo_unique_url="cloud2",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add_all([photo1, photo2])
    await db_session.flush()

    await repo.set_tags_for_photo(photo1.id, ["nature"])
    await repo.set_tags_for_photo(photo2.id, ["nature", "sunset"])

    cloud = await repo.list_cloud()

    assert cloud[0][0] == "nature"
    assert cloud[0][1] == 2