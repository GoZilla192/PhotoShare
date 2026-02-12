import pytest
from datetime import datetime

from app.models.photo import Photo
from app.mappers.photo_mapper import map_photo_to_read


class FakeCloudinary:
    def build_transformed_url(self, public_id: str, params: dict) -> str:
        if public_id is None:
            raise ValueError("public_id is required")
        return f"https://fake.cloud/{public_id}"


def test_map_photo_to_read():
    # arrange
    photo = Photo(
        id=1,
        user_id=42,
        photo_unique_url="abc123",
        cloudinary_public_id="public-id",
        description="Test photo",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
    )

    fake_cloudinary = FakeCloudinary()

    # act
    result = map_photo_to_read(photo, fake_cloudinary)

    # assert
    assert result.id == 1
    assert result.user_id == 42
    assert result.photo_unique_url == "abc123"
    assert result.photo_url == "https://fake.cloud/public-id"
    assert result.description == "Test photo"
    assert result.created_at == datetime(2024, 1, 1)
    assert result.updated_at == datetime(2024, 1, 2)


def test_map_photo_with_null_description():
    photo = Photo(
        id=10,
        user_id=5,
        photo_unique_url="null-desc",
        cloudinary_public_id="public-id",
        description=None,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    result = map_photo_to_read(photo, FakeCloudinary())

    assert result.description is None
    assert result.photo_url == "https://fake.cloud/public-id"


def test_map_photo_without_public_id_raises():
    photo = Photo(
        id=1,
        user_id=1,
        photo_unique_url="abc",
        cloudinary_public_id=None,
        description="No public id",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    fake_cloudinary = FakeCloudinary()

    with pytest.raises(ValueError):
        map_photo_to_read(photo, fake_cloudinary)