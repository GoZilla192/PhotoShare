from __future__ import annotations

from pydantic import BaseModel, Field


class RatingSetRequest(BaseModel):
    value: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    photo_id: int
    avg_rating: float | None
    ratings_count: int