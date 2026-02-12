from app.models.photo import Photo
from app.schemas.photo_schema import PhotoRead
from app.service.cloudinary_service import CloudinaryService


def map_photo_to_read(
    photo: Photo,
    cloudinary: CloudinaryService,
) -> PhotoRead:
    """
    Map ORM Photo -> API PhotoRead.
    Public representation with derived photo_url.
    """
    photo_url = cloudinary.build_transformed_url(
        public_id=photo.cloudinary_public_id,
        params={},
    )

    return PhotoRead(
        id=photo.id,
        user_id=photo.user_id,
        photo_unique_url=photo.photo_unique_url,
        description=photo.description,
        photo_url=photo_url,
        created_at=photo.created_at,
        updated_at=photo.updated_at,
    )