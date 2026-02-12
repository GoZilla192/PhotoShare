from __future__ import annotations

from pydantic import BaseModel, Field
from enum import Enum


class ShareCreateRequest(BaseModel):
    transform_params: dict = Field(default_factory=dict)


class ShareCreateResponse(BaseModel):
    uuid: str


class TransformPreset(str, Enum):
    thumb = "thumb"
    fit = "fit"
    crop = "crop"
    grayscale = "grayscale"
    sepia = "sepia"
    blur = "blur"
    rotate = "rotate"


class TransformRequest(BaseModel):
    preset: TransformPreset
    width: int | None = Field(default=None, ge=32, le=2000)
    height: int | None = Field(default=None, ge=32, le=2000)
    blur: int | None = Field(default=None, ge=1, le=200)     # лише для blur
    angle: int | None = Field(default=None, ge=-360, le=360)  # лише для rotate
    crop: str | None = Field(default=None)
    quality: str | None = Field(default=None)
    effect: str | None = Field(default=None)
