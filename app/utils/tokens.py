import pickle

import redis

from app.redis import get_from_cache, cache
from app.services import auth


async def get_token_from_cache_or_db(jti: str, type_: str, redis_instance: redis.Redis):
    token_cached = await get_from_cache(f"token:{type_}:{jti}", redis_instance)

    if token_cached:
        return pickle.loads(token_cached)

    token_db = await auth.get_token_by_jti(type_, jti)
    if token_db is None:
        return

    await cache(f"token:{type_}:{jti}", pickle.dumps(token_db), redis_instance)
    return token_db


async def remove_token_from_cache(jti: str, type_: str, redis_instance: redis.Redis):
    await redis_instance.delete(f"token:{type_}:{jti}")
