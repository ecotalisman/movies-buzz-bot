from pydantic import BaseModel


class ReviewOut(BaseModel):
    author: str
    text: str


class ScrapedMovieOut(BaseModel):
    title: str
    year: int | None
    overview: str
    reviews: list[ReviewOut]
    page_url: str


class ScraperResponse(BaseModel):
    count: int
    results: list[ScrapedMovieOut]