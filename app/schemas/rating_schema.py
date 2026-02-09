from pydantic import BaseModel, Field


class RatingSetRequest(BaseModel):
    value: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    avg: float
    count: int
