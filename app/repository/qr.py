from sqlalchemy.ext.asyncio import AsyncSession

from app.service.qr import make_qr_code
from app.repository.photos import get_photo_url_by_id


def generate_photo_qr(
    db: AsyncSession,
    photo_id: int
) -> str | None:
    """
    Generates a QR code for an image URL.
    Returns a base64 string or None if the image is not found.
    """
    photo_url = get_photo_url_by_id(db, photo_id)
    if photo_url is None:
        return None

    return make_qr_code(photo_url)