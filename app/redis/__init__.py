from redis.asyncio import Redis

from app.settings import Settings

client: Redis = Redis(
    host=Settings.REDIS_HOST,
    port=Settings.REDIS_PORT,
    password=Settings.REDIS_PASSWORD or None,
    db=Settings.REDIS_DB,
    decode_responses=True,
)

__all__ = ["client"]
