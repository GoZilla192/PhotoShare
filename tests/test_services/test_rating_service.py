import pytest
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError
from unittest.mock import AsyncMock

from app.models.photo import Photo
from app.models.rating import Rating
from app.service.rating_service import RatingService
from app.repository.ratings_repository import RatingRepository
from app.repository.photos_repository import PhotoRepository


@pytest.mark.asyncio
async def test_add_rating_photo_not_found(db_session):
    service = RatingService(
        session=db_session,
        ratings_repo=RatingRepository(db_session),
        photos_repo=PhotoRepository(db_session),
    )

    with pytest.raises(ValueError):
        await service.add_rating(photo_id=999, user_id=1, value=5)

@pytest.mark.asyncio
async def test_add_rating_own_photo(db_session):
    photos_repo = PhotoRepository(db_session)
    ratings_repo = RatingRepository(db_session)

    service = RatingService(db_session, ratings_repo, photos_repo)

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

    with pytest.raises(PermissionError):
        await service.add_rating(photo_id=photo.id, user_id=1, value=5)

@pytest.mark.asyncio
async def test_add_rating_already_exists(db_session):
    photos_repo = PhotoRepository(db_session)
    ratings_repo = RatingRepository(db_session)

    service = RatingService(db_session, ratings_repo, photos_repo)

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

    await ratings_repo.create(Rating(photo_id=photo.id, user_id=2, value=4))

    with pytest.raises(PermissionError):
        await service.add_rating(photo_id=photo.id, user_id=2, value=5)

@pytest.mark.asyncio
async def test_add_rating_integrity_error(monkeypatch, db_session):
    photos_repo = PhotoRepository(db_session)
    ratings_repo = RatingRepository(db_session)

    service = RatingService(db_session, ratings_repo, photos_repo)

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

    async def fake_create(rating):
        raise IntegrityError("", "", "")

    monkeypatch.setattr(ratings_repo, "create", fake_create)

    with pytest.raises(PermissionError):
        await service.add_rating(photo_id=photo.id, user_id=2, value=5)

@pytest.mark.asyncio
async def test_get_rating_stats_photo_not_found(db_session):
    service = RatingService(
        db_session,
        RatingRepository(db_session),
        PhotoRepository(db_session),
    )

    with pytest.raises(ValueError):
        await service.get_rating_stats(photo_id=999)

@pytest.mark.asyncio
async def test_get_rating_stats_photo_not_found(db_session):
    service = RatingService(
        db_session,
        RatingRepository(db_session),
        PhotoRepository(db_session),
    )

    with pytest.raises(ValueError):
        await service.get_rating_stats(photo_id=999)

@pytest.mark.asyncio
async def test_delete_rating_not_found(db_session):
    service = RatingService(
        db_session,
        RatingRepository(db_session),
        PhotoRepository(db_session),
    )

    with pytest.raises(ValueError):
        await service.delete_rating(rating_id=999, actor_role="admin")