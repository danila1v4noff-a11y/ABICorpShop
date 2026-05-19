from pydantic import BaseModel

class RatingCreate(BaseModel):
    rating: int

class RatingResponse(BaseModel):
    average_rating: float | None = None
    user_rating: int | None = None