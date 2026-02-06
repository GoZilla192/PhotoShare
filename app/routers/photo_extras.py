from fastapi import APIRouter, HTTPException, status

from app.schemas.rating_schema import RatingResponse, RatingSetRequest
from app.schemas.share_schema import ShareCreateResponse, ShareCreateRequest
from app.schemas.tag import PhotoTagsReadResponse, PhotoTagsSetRequest

router = APIRouter(tags=["Photo Extras"])

# --- Tags for photo: /photos/{photo_id}/tags
@router.get("/photos/{photo_id}/tags", response_model=PhotoTagsReadResponse)
async def get_photo_tags(photo_id: int):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/photos/{photo_id}/tags", response_model=PhotoTagsReadResponse)
async def set_photo_tags(photo_id: int, body: PhotoTagsSetRequest):
    # NOTE: max 5 enforced in service later
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# --- Share public link: /photos/{photo_id}/share
@router.post("/photos/{photo_id}/share", response_model=ShareCreateResponse)
async def create_share_link(photo_id: int, body: ShareCreateRequest):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# --- Public access: /public/{uuid} (+ optional /qr)
@router.get("/public/{uuid}")
async def open_public(uuid: str):
    # MVP idea: return RedirectResponse(transformed_url)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/public/{uuid}/qr")
async def get_public_qr(uuid: str):
    # Optional: return image/png
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# --- Rating: /photos/{photo_id}/rating (GET/PUT)
@router.get("/photos/{photo_id}/rating", response_model=RatingResponse)
async def get_photo_rating(photo_id: int):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/photos/{photo_id}/rating", response_model=RatingResponse)
async def set_photo_rating(photo_id: int, body: RatingSetRequest):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# --- (Optional) Transform endpoint if you want it separately from share
@router.post("/photos/{photo_id}/transform")
async def transform_photo(photo_id: int):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
