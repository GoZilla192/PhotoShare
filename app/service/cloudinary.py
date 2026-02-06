import cloudinary
import cloudinary.uploader

from app.settings import settings


cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


def upload_photo(file):
    result = cloudinary.uploader.upload(
        file,
        folder="photoshare",
        resource_type="image",
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
    }


def delete_photo(public_id: str) -> None:
    """
    Delete photo from Cloudinary by public_id
    """
    result = cloudinary.uploader.destroy(
        public_id,
        resource_type="image"
    )

    if result.get("result") not in {"ok", "not found"}:
        raise RuntimeError(f"Cloudinary delete failed: {result}")