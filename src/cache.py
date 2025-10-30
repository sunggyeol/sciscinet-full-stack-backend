import json
from redis.asyncio import Redis, ConnectionPool

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

_pool = None


async def get_redis_pool():
    """Get or create Redis connection pool."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )
    return _pool


async def get_redis():
    """Get Redis client from pool."""
    pool = await get_redis_pool()
    return Redis(connection_pool=pool)


async def close_redis_pool():
    """Close Redis connection pool."""
    global _pool
    if _pool:
        await _pool.disconnect()
        _pool = None


async def cache_json(key: str, data: dict | list):
    """Cache data as JSON string."""
    redis = await get_redis()
    await redis.set(key, json.dumps(data))
    await redis.close()


async def get_cached_json(key: str):
    """Get cached JSON data."""
    redis = await get_redis()
    data = await redis.get(key)
    await redis.close()
    return json.loads(data) if data else None
