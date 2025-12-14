# movie-service/app/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer

class Base(DeclarativeBase):
    pass

class MovieDB(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overview: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    poster_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
