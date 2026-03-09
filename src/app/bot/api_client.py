import httpx
import logging

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def search(self, query: str, limit: int = 15) -> dict:
        url = f"{self._base_url}/search"
        params = {"q": query, "limit": limit}
        logger.debug("Outgoing request: GET %s params=%s", url, params)
        return await self._get(url, params)

    async def top_tmdb(self, limit: int = 15):
        url = f"{self._base_url}/top/tmdb"
        params = {"limit": limit}
        logger.debug("Outgoing limit tmdb: GET %s params=%s", url, params)
        return await self._get(url, params)

    async def trigger_scraper(self, limit: int = 15):
        url = f"{self._base_url}/scraper/trigger"
        params = {"limit": limit}
        logger.debug("Outgoing limit scraper trigger: POST %s params=%s", url, params)
        return await self._post(url, params)

    async def scraper_status(self, task_id: str):
        url = f"{self._base_url}/scraper/status/{task_id}"
        logger.debug("Outgoing scraper status: GET %s", url)
        return await self._get(url, {})

    async def _get(self, path: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(path, params=params)
            logger.info("GET %s -> status code %s", path, r.status_code)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error("Error status %s", e)
                raise
            return r.json()

    async def _post(self, path: str, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(path, params=params)
            logger.info("POST %s -> status code %s", path, r.status_code)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error("Error status %s", e)
                raise
            return r.json()
