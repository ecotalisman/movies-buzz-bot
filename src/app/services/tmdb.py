from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import httpx


@dataclass
class TmdbMovie:
    tmdb_id: int
    title: str
    year: int | None
    rating: float | None
    overview: str
    original_title: str
    original_language: str


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

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f"{self._base_url}/search/movie", params=params)
            r.raise_for_status()
            payload = r.json()

        out: list[TmdbMovie] = []
        for item in payload.get("results", [])[:limit]:
            tmdb_id = int(item["id"])
            title = item.get("title") or item.get("name") or "(без назви)"
            rating = item.get("vote_average")
            overview = item.get("overview") or ""
            original_title = item.get("original_title") or ""
            original_language = item.get("original_language") or ""
            year = None

            rd = item.get("release_date")
            if rd:
                try:
                    year = date.fromisoformat(rd).year
                except ValueError:
                    year = None

            out.append(
                TmdbMovie(
                    tmdb_id=tmdb_id,
                    title=title,
                    year=year,
                    rating=rating,
                    overview=overview,
                    original_title=original_title,
                    original_language=original_language,
                )
            )

        return out
