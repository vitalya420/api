from typing import Any

import redis.asyncio as redis

from app.config import config


async def connect() -> redis.Redis:
    redis_ = redis.Redis(
        host=config['REDIS_HOST'],
        port=config['REDIS_PORT'],
        username='default',
        password=config['REDIS_PASSWORD'],
        db=config['REDIS_DB'],
    )
    return redis_


async def cache(key: str, value: Any, redis_instance: redis.Redis):
    await redis_instance.set(key, value, ex=3600)


async def get_from_cache(key: str, redis_instance: redis.Redis) -> Any:
    return await redis_instance.get(key)


async def remove_from_cache(key: str, redis_instance: redis.Redis):
    await redis_instance.delete(key)
