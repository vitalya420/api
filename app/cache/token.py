import pickle
from typing import Union, Literal

from redis.asyncio import Redis

from app.models import AccessToken, RefreshToken
from app.services import tokens_service

ONE_HOUR = 60 * 60


async def save_token_to_cache(
        token: Union[AccessToken, RefreshToken],
        redis: Redis,
        expires_in: int = ONE_HOUR):
    if not isinstance(token, RefreshToken) and not isinstance(token, AccessToken):
        raise TypeError("Token should be model instance")

    type_ = "access" if isinstance(token, AccessToken) else "refresh"

    key = f"token:{type_}:{token.jti}"
    value = pickle.dumps(token)

    await redis.set(key, value, ex=expires_in)


async def get_token_from_cache(
        jti: str, redis: Redis,
        type_: Union[str, Literal["access", "refresh"]] = "access"):
    key = f"token:{type_}:{jti}"
    value = await redis.get(key)
    if value:
        return pickle.loads(value)


async def get_token_from_cache_or_db(
        jti: str, redis: Redis,
        type_: Union[str, Literal["access", "refresh"]] = "access"):
    cached = await get_token_from_cache(jti, redis, type_)

    if cached:
        return cached
    token_db = await tokens_service.get_access_token_by_jti(jti)

    if token_db:
        await save_token_to_cache(token_db, redis)
        return token_db


async def delete_token_from_cache(
        jti: str, redis: Redis,
        type_: Union[str, Literal["access", "refresh"]] = "access"):
    await redis.delete(f"token:{type_}:{jti}")
