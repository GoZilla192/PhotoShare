from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from app.core.settings import Settings
from app.schemas.share_schema import TransformRequest


@dataclass(frozen=True)
class CloudinaryPreset:
    crop: str | None = None
    width: int | None = None
    height: int | None = None
    effect: str | None = None
    angle: int | None = None

class CloudinaryService:
    """
    Thin wrapper around Cloudinary SDK.
    Keeps config in one place and exposes app-level operations.
    """

    def __init__(self, settings: Settings) -> None:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )

    def upload_photo(self, file: bytes, folder: str = "photoshare") -> dict[str, Any]:
        """
        Upload file-like object or bytes to Cloudinary.
        Returns: {"url": "...", "public_id": "..."}
        """
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
        )
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
        }

    def delete_photo(self, public_id: str) -> None:
        """
        Best-effort delete; treat 'not found' as OK.
        """
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        if result.get("result") not in {"ok", "not found"}:
            raise RuntimeError(f"Cloudinary delete failed: {result}")

    def build_transformed_url(self, public_id: str, params: dict[str, Any]) -> str:
        """
        Build a Cloudinary URL for a public_id with transformations.
        params example: {"width": 400, "height": 400, "crop": "fill", "effect": "grayscale"}
        """
        url, _ = cloudinary.utils.cloudinary_url(public_id, transformation=[params] if params else None)
        return url

def build_transform_params(req: TransformRequest) -> dict[str, Any]:
    """
    Convert API TransformRequest into Cloudinary transformation dict.
    Cloudinary Python SDK expects keys like: crop/width/height/effect/angle, etc.
    """
    params: dict[str, Any] = {}
    if req.crop:
        params["crop"] = req.crop
    if req.width is not None:
        params["width"] = req.width
    if req.height is not None:
        params["height"] = req.height
    if req.effect:
        params["effect"] = req.effect
    if req.angle is not None:
        params["angle"] = req.angle
    return params

