from pydantic import BaseModel, Field


class MovieShort(BaseModel):
    tmdb_id: int
    title: str
    year: int | None = None
    rating: float | None = Field(default=None, description="TMDB vote_average")
    one_liner: str
    tmdb_url: str


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[MovieShort]
