from pydantic import BaseModel, conint


class RatingCreate(BaseModel):
    value: conint(ge=1, le=5)


class RatingStats(BaseModel):
    avg: float | None
    count: int