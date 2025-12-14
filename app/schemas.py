# movie-service/app/schemas.py
from pydantic import BaseModel, ConfigDict

class MovieCreate(BaseModel):
    title: str
    tmdb_id: int | None = None
    release_year: int | None = None
    overview: str | None = None
    poster_url: str | None = None

class MovieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    tmdb_id: int | None = None
    release_year: int | None = None
    overview: str | None = None
    poster_url: str | None = None
