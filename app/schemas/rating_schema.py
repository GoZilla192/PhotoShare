from pydantic import BaseModel, Field


class RatingSetRequest(BaseModel):
    rating: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    photo_id: int
    avg_rating: float
    ratings_count: int
    my_rating: int | None = None
