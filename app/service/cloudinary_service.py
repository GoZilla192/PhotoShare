from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from app.settings import Settings


class CloudinaryTransformError:
    pass

@dataclass(frozen=True)
class TransformPreset:
    name: str
    params: dict

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
        PRESETS: dict[str, TransformPreset] = {
            "thumb_300": TransformPreset("thumb_300", {"width": 300, "height": 300, "crop": "fill"}),
            "grayscale": TransformPreset("grayscale", {"effect": "grayscale"}),
            "sepia": TransformPreset("sepia", {"effect": "sepia"}),
            "blur": TransformPreset("blur", {"effect": "blur:300"}),
            "rotate_90": TransformPreset("rotate_90", {"angle": 90}),
        }

    def upload_photo(self, file: Any, *, folder: str = "photoshare") -> dict[str, str]:
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

    def build_transformed_url(self, *, public_id: str, params: dict) -> str:
        """
        Build a Cloudinary URL for a public_id with transformations.
        params example: {"width": 400, "height": 400, "crop": "fill", "effect": "grayscale"}
        """
        # Cloudinary expects transformations as keyword args.
        # We force secure=True so it's https.
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            secure=True,
            **params,
        )
        return url

    def get_allowed_presets(self) -> list[str]:
        return list(self.PRESETS.keys())

    def build_transformed_url_preset(self, *, public_id: str, preset: str) -> str:
        p = self.PRESETS.get(preset)
        if not p:
            raise CloudinaryTransformError(f"Unknown preset: {preset}")

        return self.build_transformed_url(public_id=public_id, params=p.params)