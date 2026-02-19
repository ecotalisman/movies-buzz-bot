from fastapi import APIRouter, Query

from src.app.settings import settings
from src.app.schemas.movie import SearchResponse, MovieShort
from src.app.services.summarize import one_sentence
from src.app.services.tmdb import TmdbClient
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/top/tmdb", response_model=SearchResponse)
async def search_top(
        limit: int = Query(default=10, ge=1, le=20),
) -> SearchResponse:

    logger.info("Search top rated: limit=%d", limit)
    client = TmdbClient(api_key=settings.tmdb_api_key, language=settings.tmdb_language)
    primary = await client.discover_top(limit=limit, language=settings.tmdb_language)

    logger.info("Top rated: %d results", len(primary))
    results: list[MovieShort] = []
    genres = await client.get_genres()

    for m in primary:
        results.append(
            MovieShort(
                tmdb_id=m.tmdb_id,
                title=m.title,
                year=m.year,
                rating=m.rating,
                one_liner=one_sentence(m.overview),
                tmdb_url=f"https://www.themoviedb.org/movie/{m.tmdb_id}",
                genres=[genres[gid] for gid in m.genre_ids if gid in genres],
            )
        )

    return SearchResponse(query="top_rated", count=len(results), results=results)
