from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import httpx
import logging

logger = logging.getLogger(__name__)
_genres_cache: dict[int, str] = {}


@dataclass
class TmdbMovie:
    tmdb_id: int
    title: str
    year: int | None
    rating: float | None
    overview: str
    original_title: str
    original_language: str
    genre_ids: list[int]


class TmdbClient:
    def __init__(self, api_key: str, language: str = "uk-UA") -> None:
        self._api_key = api_key
        self._language = language
        self._base_url = "https://api.themoviedb.org/3"

    async def search_movies(
            self,
            query: str,
            *,
            limit: int = 10,
            language: str | None = None,
    ) -> list[TmdbMovie]:
        lang = language or self._language

        params = {
            "api_key": self._api_key,
            "query": query,
            "include_adult": "false",
            "language": lang,
            "page": 1,
        }

        logger.debug("TMDB search: query=%s, language=%s", query, lang)

        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self._base_url}/search/movie"
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        results = payload.get("results", [])
        logger.info("TMDB returned %d results for query='%s' (status=%d)", len(results), query, r.status_code)
        return [self._parse_movie(item) for item in results[:limit]]

    async def discover_top(self,
                           limit: int = 15,
                           language: str | None = None,
                           ) -> list[TmdbMovie]:
        lang = language or self._language

        date_to = date.today()
        date_from = date_to - timedelta(days=90)
        params = {
            "api_key": self._api_key,
            "language": lang,
            "page": 1,
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50,
            "primary_release_date.gte": date_from.isoformat(),
            "primary_release_date.lte": date_to.isoformat(),
        }

        logger.debug("TMDB top_rated: limit=%d, language=%s", limit, lang)

        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self._base_url}/discover/movie"
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        results = payload.get("results", [])
        logger.info("TMDB returned %d results for limit='%d' (status=%d)", len(results), limit, r.status_code)
        return [self._parse_movie(item) for item in results[:limit]]

    async def get_genres(self, language=None) -> dict[int, str]:
        from src.app.services.redis_cache import get_cached_genres, set_cached_genres

        if _genres_cache:
            return _genres_cache

        try:
            cached = await get_cached_genres()
            if cached:
                _genres_cache.update(cached)
                logger.info("Loaded %d genres from Redis cache", len(cached))
                return cached
        except Exception:
            logger.warning("Redis unavailable, falling through to TMDB API", exc_info=True)

        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self._base_url}/genre/movie/list"
            lang = language or self._language
            params = {
                "api_key": self._api_key,
                "language": lang,
            }
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        genres_list = payload.get("genres", [])
        genre_map = {genre["id"]: genre["name"] for genre in genres_list}
        logger.info("TMDB returned %s genres", len(genres_list))
        _genres_cache.update(genre_map)

        try:
            await set_cached_genres(genre_map)
        except Exception:
            logger.warning("Failed to cache genres in Redis", exc_info=True)

        return genre_map

    def _parse_movie(self, item: dict) -> TmdbMovie:
        year = None
        rd = item.get("release_date")
        if rd:
            try:
                year = date.fromisoformat(rd).year
            except ValueError as e:
                logger.error("TMDB API error: %s", e, exc_info=True)

        return TmdbMovie(
            tmdb_id=int(item["id"]),
            title=item.get("title") or item.get("name") or "(untitled)",
            year=year,
            rating=item.get("vote_average"),
            overview=item.get("overview") or "",
            original_title=item.get("original_title") or "",
            original_language=item.get("original_language") or "",
            genre_ids=item.get("genre_ids", [])
        )
