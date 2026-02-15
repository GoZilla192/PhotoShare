import pytest
from datetime import datetime, UTC
from types import SimpleNamespace

from app.core.exceptions import NotFoundError
from app.repository.transformed_images_repository import TransformedImageRepository
from app.models.photo import Photo
from app.models.public_link import PublicLink
from app.models.transformed_image import TransformedImage
from app.service.share_service import ShareService
from app.repository.photos_repository import PhotoRepository
from app.repository.public_links_repository import PublicLinkRepository


@pytest.mark.asyncio
async def test_create_share_link_photo_not_found(db_session):
    service = ShareService(
        session=db_session,
        photos_repo=PhotoRepository(db_session),
        transformed_repo=TransformedImageRepository(db_session),
        cloudinary=MockCloudinary(),
        public_links_repo=PublicLinkRepository(db_session),
        qr_maker=MockQr(),
    )

    with pytest.raises(NotFoundError):
        await service.create_share_link(
            photo_id=999,
            transform_params={},
            current_user=SimpleNamespace(id=1),
        )

class MockCloudinary:
    def build_transformed_url(self, public_id, params):
        return "https://example.com/transformed.jpg"

class MockQr:
    def make_png_base64(self, url):
        return "qr"

@pytest.mark.asyncio
async def test_create_share_link_success(db_session):
    photos_repo = PhotoRepository(db_session)
    transformed_repo = TransformedImageRepository(db_session)
    public_links_repo = PublicLinkRepository(db_session)

    cloudinary = MockCloudinary()
    qr = MockQr()

    service = ShareService(
        session=db_session,
        photos_repo=photos_repo,
        transformed_repo=transformed_repo,
        cloudinary=cloudinary,
        public_links_repo=public_links_repo,
        qr_maker=qr,
    )

    photo = Photo(
        user_id=1,
        photo_unique_url="share",
        cloudinary_public_id="abc",
        description="Test",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    db_session.add(photo)
    await db_session.flush()

    uuid = await service.create_share_link(
        photo_id=photo.id,
        transform_params={"width": 100},
        current_user=SimpleNamespace(id=1),
    )

    assert isinstance(uuid, str)

@pytest.mark.asyncio
async def test_resolve_public_not_found(db_session):
    service = ShareService(
        session=db_session,
        photos_repo=None,
        transformed_repo=None,
        cloudinary=None,
        public_links_repo=PublicLinkRepository(db_session),
        qr_maker=None,
    )

    with pytest.raises(NotFoundError):
        await service.resolve_public(uuid="unknown")

@pytest.mark.asyncio
async def test_resolve_public_success(db_session):
    public_links_repo = PublicLinkRepository(db_session)

    service = ShareService(
        session=db_session,
        photos_repo=None,
        transformed_repo=None,
        cloudinary=None,
        public_links_repo=public_links_repo,
        qr_maker=None,
    )

    ti = TransformedImage(
        photo_id=1,
        image_url="https://example.com/x.jpg",
        transformation="{}",
    )

    db_session.add(ti)
    await db_session.flush()

    link = PublicLink(
        uuid="123",
        transformed_image_id=ti.id,
        qr_code_url="dummy",
    )
    db_session.add(link)
    await db_session.flush()

    url = await service.resolve_public(uuid="123")

    assert url == "https://example.com/x.jpg"

@pytest.mark.asyncio
async def test_make_public_qr(db_session):
    qr = MockQr()

    service = ShareService(
        session=db_session,
        photos_repo=None,
        transformed_repo=None,
        cloudinary=None,
        public_links_repo=None,
        qr_maker=qr,
    )

    result = await service.make_public_qr(uuid="abc")

    assert result == "qr"