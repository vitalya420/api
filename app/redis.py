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

