from __future__ import annotations

from dataclasses import dataclass
from datetime import date

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

        out: list[TmdbMovie] = []
        for item in payload.get("results", [])[:limit]:
            tmdb_id = int(item["id"])
            title = item.get("title") or item.get("name") or "(untitled)"
            rating = item.get("vote_average")
            overview = item.get("overview") or ""
            original_title = item.get("original_title") or ""
            original_language = item.get("original_language") or ""
            year = None
            genre_ids = item.get("genre_ids", [])

            rd = item.get("release_date")
            if rd:
                try:
                    year = date.fromisoformat(rd).year
                except ValueError as e:
                    year = None
                    logger.error("TMDB API error: %s", e, exc_info=True)

            out.append(
                TmdbMovie(
                    tmdb_id=tmdb_id,
                    title=title,
                    year=year,
                    rating=rating,
                    overview=overview,
                    original_title=original_title,
                    original_language=original_language,
                    genre_ids=genre_ids,
                )
            )

        return out

    async def get_genres(self, language=None) -> dict[int, str]:
        if _genres_cache:
            return _genres_cache

        async with httpx.AsyncClient(timeout=15) as client:
            url = f"{self._base_url}/genre/movie/list"
            params = {
                "api_key": self._api_key,
                "language": self._language,
            }
            r = await client.get(url, params=params)
            r.raise_for_status()
            payload = r.json()

        genres_list = payload.get("genres", [])
        genre_map = {genre["id"]: genre["name"] for genre in genres_list}
        logger.info("TMDB returned %s genres", len(genres_list))
        _genres_cache.update(genre_map)

        return genre_map
