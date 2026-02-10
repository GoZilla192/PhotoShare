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
    Applies preset defaults, then allows explicit fields to override.
    """
    params: dict[str, Any] = {}

    # --- Preset defaults ---
    # Note: keep these conservative; explicit fields can override below.
    if req.preset == "thumb":
        params.update({"crop": "thumb", "width": req.width or 200, "height": req.height or 200})
    elif req.preset == "fit":
        params.update({"crop": "fit", "width": req.width or 800})
        if req.height is not None:
            params["height"] = req.height
    elif req.preset == "crop":
        params.update({"crop": "fill", "width": req.width or 800, "height": req.height or 800})
    elif req.preset == "grayscale":
        params.update({"effect": "grayscale"})
    elif req.preset == "sepia":
        params.update({"effect": "sepia"})
    elif req.preset == "blur":
        # Cloudinary supports blur effect like "blur:200"
        if req.blur is not None:
            params.update({"effect": f"blur:{req.blur}"})
        else:
            params.update({"effect": "blur:100"})
    elif req.preset == "rotate":
        if req.angle is not None:
            params.update({"angle": req.angle})
        else:
            params.update({"angle": 90})

    # --- Explicit overrides (if provided) ---
    if req.crop:
        params["crop"] = req.crop
    if req.width is not None:
        params["width"] = req.width
    if req.height is not None:
        params["height"] = req.height
    if req.quality:
        params["quality"] = req.quality
    if req.effect:
        params["effect"] = req.effect
    # rotate-specific explicit override
    if req.angle is not None:
        params["angle"] = req.angle
    # blur-specific explicit override (takes priority over preset blur)
    if req.blur is not None and (req.preset == "blur"):
        params["effect"] = f"blur:{req.blur}"

    return params

