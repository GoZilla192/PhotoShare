import pytest

from datetime import datetime, UTC
from app.repository.photos_repository import PhotoRepository
from app.models.photo import Photo
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.photo_tags import PhotoTag

@pytest.mark.asyncio
async def test_get_by_id(db_session):
    repo = PhotoRepository(db_session)

    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="test",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    result = await repo.get_by_id(1)
    assert result is not None
    assert result.photo_unique_url == "test"

    not_found = await repo.get_by_id(999)
    assert not_found is None

@pytest.mark.asyncio
async def test_update_description(db_session):
    repo = PhotoRepository(db_session)

    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="update-test",
        cloudinary_public_id="dummy",
        description="Old",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    updated = await repo.update_description(1, "New")
    assert updated is not None
    assert updated.description == "New"

    missing = await repo.update_description(999, "X")
    assert missing is None

@pytest.mark.asyncio
async def test_delete_by_id(db_session):
    repo = PhotoRepository(db_session)

    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="delete-test",
        cloudinary_public_id="dummy",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    deleted = await repo.delete_by_id(1)
    assert deleted is True

    missing = await repo.delete_by_id(999)
    assert missing is False

@pytest.mark.asyncio
async def test_list_and_count_by_user(db_session):
    repo = PhotoRepository(db_session)

    # user 1
    for i in range(5):
        db_session.add(
            Photo(
                user_id=1,
                photo_unique_url=f"user1-{i}",
                cloudinary_public_id="dummy",
                description="Test",
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

    # user 2
    db_session.add(
        Photo(
            user_id=2,
            photo_unique_url="user2",
            cloudinary_public_id="dummy",
            description="Other",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    await db_session.flush()

    photos = await repo.list_by_user(user_id=1, limit=10, offset=0)
    assert len(photos) == 5

    count = await repo.count_by_user(user_id=1)
    assert count == 5

    # check limit
    limited = await repo.list_by_user(user_id=1, limit=2, offset=0)
    assert len(limited) == 2

    # check offset
    offset = await repo.list_by_user(user_id=1, limit=10, offset=2)
    assert len(offset) == 3

@pytest.mark.asyncio
async def test_search_without_filters(db_session):
    repo = PhotoRepository(db_session)

    db_session.add(
        Photo(
            user_id=1,
            photo_unique_url="search-1",
            cloudinary_public_id="dummy",
            description="Hello world",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    await db_session.flush()

    results = await repo.search(limit=10, offset=0)

    assert len(results) == 1

@pytest.mark.asyncio
async def test_search_by_text_query(db_session):
    repo = PhotoRepository(db_session)

    db_session.add(
        Photo(
            user_id=1,
            photo_unique_url="search-text",
            cloudinary_public_id="dummy",
            description="Beautiful sunset",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    await db_session.flush()

    results = await repo.search(q="sunset", limit=10, offset=0)

    assert len(results) == 1

    results_empty = await repo.search(q="mountain", limit=10, offset=0)
    assert len(results_empty) == 0

@pytest.mark.asyncio
async def test_search_with_min_rating(db_session):
    repo = PhotoRepository(db_session)

    photo = Photo(
        user_id=1,
        photo_unique_url="rated-photo",
        cloudinary_public_id="dummy",
        description="Rated",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    db_session.add(
        Rating(photo_id=photo.id, user_id=2, value=5)
    )

    await db_session.flush()

    results = await repo.search(min_rating=4, limit=10, offset=0)
    assert len(results) == 1

    results_empty = await repo.search(min_rating=6, limit=10, offset=0)
    assert len(results_empty) == 0

@pytest.mark.asyncio
async def test_search_sort_top(db_session):
    repo = PhotoRepository(db_session)

    photo1 = Photo(
        user_id=1,
        photo_unique_url="top1",
        cloudinary_public_id="dummy",
        description="Top 1",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    photo2 = Photo(
        user_id=1,
        photo_unique_url="top2",
        cloudinary_public_id="dummy",
        description="Top 2",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add_all([photo1, photo2])
    await db_session.flush()

    # додаємо рейтинги
    db_session.add(Rating(photo_id=photo1.id, user_id=2, value=5))
    db_session.add(Rating(photo_id=photo2.id, user_id=2, value=2))
    await db_session.flush()

    results = await repo.search(sort="top", limit=10, offset=0)

    assert results[0].photo_unique_url == "top1"

@pytest.mark.asyncio
async def test_search_with_date_filter(db_session):
    repo = PhotoRepository(db_session)

    old_photo = Photo(
        user_id=1,
        photo_unique_url="old",
        cloudinary_public_id="dummy",
        description="Old",
        created_at=datetime(2020, 1, 1, tzinfo=UTC),
        updated_at=datetime(2020, 1, 1, tzinfo=UTC),
    )

    new_photo = Photo(
        user_id=1,
        photo_unique_url="new",
        cloudinary_public_id="dummy",
        description="New",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add_all([old_photo, new_photo])
    await db_session.flush()

    results = await repo.search(
        date_from=datetime(2021, 1, 1, tzinfo=UTC),
        limit=10,
        offset=0,
    )

    assert len(results) == 1
    assert results[0].photo_unique_url == "new"

@pytest.mark.asyncio
async def test_search_by_tag(db_session):
    repo = PhotoRepository(db_session)

    tag = Tag(name="nature")

    photo = Photo(
        user_id=1,
        photo_unique_url="tag-photo",
        cloudinary_public_id="dummy",
        description="Tagged",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add_all([tag, photo])
    await db_session.flush()

    db_session.add(
        PhotoTag(photo_id=photo.id, tag_id=tag.id)
    )
    await db_session.flush()

    results = await repo.search(tag="nature", limit=10, offset=0)

    assert len(results) == 1

    empty = await repo.search(tag="unknown", limit=10, offset=0)
    assert len(empty) == 0

@pytest.mark.asyncio
async def test_search_default_sorting(db_session):
    repo = PhotoRepository(db_session)

    older = Photo(
        user_id=1,
        photo_unique_url="older",
        cloudinary_public_id="dummy",
        description="Old",
        created_at=datetime(2020, 1, 1, tzinfo=UTC),
        updated_at=datetime(2020, 1, 1, tzinfo=UTC),
    )

    newer = Photo(
        user_id=1,
        photo_unique_url="newer",
        cloudinary_public_id="dummy",
        description="New",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add_all([older, newer])
    await db_session.flush()

    results = await repo.search(limit=10, offset=0)

    assert results[0].photo_unique_url == "newer"

@pytest.mark.asyncio
async def test_count_search_without_filters(db_session):
    repo = PhotoRepository(db_session)

    db_session.add(
        Photo(
            user_id=1,
            photo_unique_url="count-1",
            cloudinary_public_id="dummy",
            description="Test",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    await db_session.flush()

    count = await repo.count_search()
    assert count == 1

@pytest.mark.asyncio
async def test_count_search_with_text_filter(db_session):
    repo = PhotoRepository(db_session)

    db_session.add(
        Photo(
            user_id=1,
            photo_unique_url="count-text",
            cloudinary_public_id="dummy",
            description="Beautiful forest",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )

    await db_session.flush()

    count = await repo.count_search(q="forest")
    assert count == 1

    empty = await repo.count_search(q="mountain")
    assert empty == 0

@pytest.mark.asyncio
async def test_count_search_by_tag(db_session):
    repo = PhotoRepository(db_session)

    tag = Tag(name="nature")
    photo = Photo(
        user_id=1,
        photo_unique_url="count-tag",
        cloudinary_public_id="dummy",
        description="Tagged",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add_all([tag, photo])
    await db_session.flush()

    db_session.add(PhotoTag(photo_id=photo.id, tag_id=tag.id))
    await db_session.flush()

    count = await repo.count_search(tag="nature")
    assert count == 1