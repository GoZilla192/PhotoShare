from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.service.qr import generate_photo_qr

router = APIRouter(
    prefix="/qr",
    tags=["QR"]
)


@router.get("/photos/{photo_id}")
def get_photo_qr(
    photo_id: int,
    db: Session = Depends(get_db),
):
    qr_code = generate_photo_qr(db, photo_id)

    if qr_code is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    return {
        "qr_code_base64": qr_code
    }