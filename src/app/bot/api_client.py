import httpx
import logging

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def search(self, query: str, limit: int = 10) -> dict:
        params = {"q": query, "limit": limit}
        url = f"{self._base_url}/search"

        logger.debug("Outgoing request: GET %s params=%s", url, params)

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, params=params)
            logger.info("Status code %s", r.status_code)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error("Error status %s", e)
                raise
            return r.json()
