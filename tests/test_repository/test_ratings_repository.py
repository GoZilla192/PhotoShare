import pytest

from app.repository.ratings_repository import RatingRepository
from app.models.rating import Rating


@pytest.mark.asyncio
async def test_get_by_photo_and_user(db_session):
    repo = RatingRepository(db_session)

    rating = Rating(photo_id=1, user_id=1, value=5)
    db_session.add(rating)
    await db_session.flush()

    found = await repo.get_by_photo_and_user(1, 1)
    assert found is not None
    assert found.value == 5

    missing = await repo.get_by_photo_and_user(1, 999)
    assert missing is None

@pytest.mark.asyncio
async def test_get_rating_by_id(db_session):
    repo = RatingRepository(db_session)

    rating = Rating(photo_id=1, user_id=1, value=4)
    db_session.add(rating)
    await db_session.flush()

    found = await repo.get_by_id(rating.id)
    assert found is not None

    missing = await repo.get_by_id(999)
    assert missing is None

@pytest.mark.asyncio
async def test_get_rating_by_id(db_session):
    repo = RatingRepository(db_session)

    rating = Rating(photo_id=1, user_id=1, value=4)
    db_session.add(rating)
    await db_session.flush()

    found = await repo.get_by_id(rating.id)
    assert found is not None

    missing = await repo.get_by_id(999)
    assert missing is None

@pytest.mark.asyncio
async def test_create_rating(db_session):
    repo = RatingRepository(db_session)

    rating = Rating(photo_id=1, user_id=1, value=3)

    created = await repo.create(rating)

    assert created.id is not None

@pytest.mark.asyncio
async def test_delete_rating(db_session):
    repo = RatingRepository(db_session)

    rating = Rating(photo_id=1, user_id=1, value=2)
    db_session.add(rating)
    await db_session.flush()

    await repo.delete(rating)

    deleted = await repo.get_by_id(rating.id)
    assert deleted is None

@pytest.mark.asyncio
async def test_get_rating_stats(db_session):
    repo = RatingRepository(db_session)

    # w/o ratings
    empty = await repo.get_rating_stats(photo_id=1)
    assert empty["ratings_count"] == 0
    assert empty["avg_rating"] is None

    # with ratings
    db_session.add_all([
        Rating(photo_id=1, user_id=1, value=4),
        Rating(photo_id=1, user_id=2, value=2),
    ])
    await db_session.flush()

    stats = await repo.get_rating_stats(photo_id=1)

    assert stats["ratings_count"] == 2
    assert stats["avg_rating"] == 3.0