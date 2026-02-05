from fastapi import APIRouter, Query

from src.app.schemas.movie import MovieShort, SearchResponse
from src.app.services.summarize import one_sentence
from src.app.services.tmdb import TmdbClient
from src.app.settings import settings

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1, max_length=120, description="Search query"),
    limit: int = Query(default=10, ge=1, le=10),
    year_from: int | None = Query(default=None, ge=1900, le=2100),
    year_to: int | None = Query(default=None, ge=1900, le=2100),
) -> SearchResponse:
    client = TmdbClient(api_key=settings.tmdb_api_key, language=settings.tmdb_language)
    movies = await client.search_movies(q, limit=limit * 3)

    if year_from is not None or year_to is not None:
        yf = year_from if year_from is not None else 1900
        yt = year_to if year_to is not None else 2100
        movies = [m for m in movies if (m.year is not None and yf <= m.year <= yt)]

    movies = movies[:limit]

    results: list[MovieShort] = []
    for m in movies:
        results.append(
            MovieShort(
                tmdb_id=m.tmdb_id,
                title=m.title,
                year=m.year,
                rating=m.rating,
                one_liner=one_sentence(m.overview),
                tmdb_url=f"https://www.themoviedb.org/movie/{m.tmdb_id}",
            )
        )

    return SearchResponse(query=q, count=len(results), results=results)
