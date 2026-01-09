from pydantic import BaseModel, ConfigDict
from typing import Annotated
from annotated_types import Ge, Le

ratingInt = Annotated[int, Ge(1), Le(10)]

class ReviewCreate(BaseModel):
    user_id: int
    tmdb_movie_id: int
    rating: ratingInt
    review_text: str

class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    tmdb_movie_id: int
    rating: ratingInt
    review_text: str
