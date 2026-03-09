import json
import redis.asyncio as aioredis

from src.app.settings import settings

_client = None


async def get_redis():
    global _client
    if _client is None:
        _client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _client


async def close_redis():
    global _client
    if _client is not None:
        await _client.close()
        _client = None


async def get_cached_genres():
    redis = await get_redis()
    data = await redis.get("tmdb:genres")
    if data is None:
        return None
    genres_dict = json.loads(data)
    return {int(k): v for k, v in genres_dict.items()}


async def set_cached_genres(genres, ttl=86400):
    redis = await get_redis()
    genres_json = json.dumps(genres)
    return await redis.set("tmdb:genres", genres_json, ex=ttl)
