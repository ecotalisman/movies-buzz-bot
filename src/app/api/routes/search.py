from fastapi import APIRouter, Query

from src.app.schemas.movie import MovieShort, SearchResponse
from src.app.services.summarize import one_sentence
from src.app.services.tmdb import TmdbClient
from src.app.settings import settings

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def is_unlocalized_title(movie) -> bool:
    if not movie.title:
        return True
    if movie.original_title and movie.title.strip() == movie.original_title.strip():
        return True
    return False


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1, max_length=120, description="Search query"),
    limit: int = Query(default=10, ge=1, le=10),
    year_from: int | None = Query(default=None, ge=1900, le=2100),
    year_to: int | None = Query(default=None, ge=1900, le=2100),
) -> SearchResponse:
    logger.info("Search request: q='%s', limit=%d", q, limit)
    client = TmdbClient(api_key=settings.tmdb_api_key, language=settings.tmdb_language)

    fetch_limit = limit * 5

    primary = await client.search_movies(q, limit=fetch_limit, language=settings.tmdb_language)

    fallback = []
    if settings.tmdb_fallback_language:
        fallback = await client.search_movies(q, limit=fetch_limit, language=settings.tmdb_fallback_language)

    fallback_by_id = {m.tmdb_id: m for m in fallback}

    movies = primary[:] if primary else fallback[:]
    for m in movies:
        if not m.overview:
            fm = fallback_by_id.get(m.tmdb_id)
            if fm and fm.overview:
                m.overview = fm.overview

        fm = fallback_by_id.get(m.tmdb_id)

        if fm and (not m.overview) and fm.overview:
            m.overview = fm.overview

        if fm and is_unlocalized_title(m) and fm.title:
            m.title = fm.title

    if year_from is not None or year_to is not None:
        yf = year_from if year_from is not None else 1900
        yt = year_to if year_to is not None else 2100
        movies = [m for m in movies if (m.year is not None and yf <= m.year <= yt)]

    logger.info("Search '%s' -> %d results", q, len(movies))

    movies = movies[:limit]

    results: list[MovieShort] = []
    genres = await client.get_genres()

    for m in movies:
        results.append(
            MovieShort(
                tmdb_id=m.tmdb_id,
                title=m.title,
                year=m.year,
                rating=m.rating,
                one_liner=one_sentence(m.overview),
                tmdb_url=f"https://www.themoviedb.org/movie/{m.tmdb_id}",
                genres=[genres[gid] for gid in m.genre_ids if gid in genres]
            )
        )

    return SearchResponse(query=q, count=len(results), results=results)
