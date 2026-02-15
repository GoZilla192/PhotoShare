import pytest

from app.service.cloudinary_service import CloudinaryService, TransformRequest, build_transform_params
from app.core.settings import Settings



@pytest.mark.asyncio
async def test_upload_photo(monkeypatch):
    class FakeUploader:
        @staticmethod
        def upload(file, folder, resource_type):
            return {
                "secure_url": "https://example.com/img.jpg",
                "public_id": "abc123",
            }

    monkeypatch.setattr("cloudinary.uploader.upload", FakeUploader.upload)

    settings = Settings(
        CLOUDINARY_NAME="x",
        CLOUDINARY_API_KEY="x",
        CLOUDINARY_API_SECRET="x",
    )

    service = CloudinaryService(settings)

    result = service.upload_photo(b"file")

    assert result["url"] == "https://example.com/img.jpg"
    assert result["public_id"] == "abc123"

def test_delete_photo_success(monkeypatch):
    def fake_destroy(public_id, resource_type):
        return {"result": "ok"}

    monkeypatch.setattr("cloudinary.uploader.destroy", fake_destroy)

    settings = Settings(...)
    service = CloudinaryService(settings)

    service.delete_photo("abc")  # не має кидати

def test_delete_photo_error(monkeypatch):
    def fake_destroy(public_id, resource_type):
        return {"result": "error"}

    monkeypatch.setattr("cloudinary.uploader.destroy", fake_destroy)

    settings = Settings(...)
    service = CloudinaryService(settings)

    with pytest.raises(RuntimeError):
        service.delete_photo("abc")

def test_build_transformed_url(monkeypatch):
    def fake_cloudinary_url(public_id, transformation):
        return ("https://example.com/url", {})

    monkeypatch.setattr("cloudinary.utils.cloudinary_url", fake_cloudinary_url)

    settings = Settings(...)
    service = CloudinaryService(settings)

    url = service.build_transformed_url("abc", {"width": 100})

    assert url == "https://example.com/url"

def test_build_transformed_url(monkeypatch):
    def fake_cloudinary_url(public_id, transformation):
        return ("https://example.com/url", {})

    monkeypatch.setattr("cloudinary.utils.cloudinary_url", fake_cloudinary_url)

    settings = Settings(...)
    service = CloudinaryService(settings)

    url = service.build_transformed_url("abc", {"width": 100})

    assert url == "https://example.com/url"

def test_build_transform_params_thumb():
    req = TransformRequest(preset="thumb", width=None, height=None)
    params = build_transform_params(req)

    assert params["crop"] == "thumb"
    assert params["width"] == 200
    assert params["height"] == 200

def test_build_transform_params_rotate_default():
    req = TransformRequest(preset="rotate", angle=None)
    params = build_transform_params(req)

    assert params["angle"] == 90

def test_build_transform_params_override():
    req = TransformRequest(
        preset="thumb",
        width=500,
        crop="fill",
    )

    params = build_transform_params(req)

    assert params["width"] == 500
    assert params["crop"] == "fill"