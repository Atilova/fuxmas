import redis.asyncio as aioredis

from src.common.config import redis_config


def redis_client_factory(db: int = 0) -> aioredis.Redis:
    return aioredis.Redis.from_url(redis_config.url(db=db))
