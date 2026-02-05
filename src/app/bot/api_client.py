import httpx


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def search(self, query: str, limit: int = 10) -> dict:
        params = {"q": query, "limit": limit}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{self._base_url}/search", params=params)
            r.raise_for_status()
            return r.json()
