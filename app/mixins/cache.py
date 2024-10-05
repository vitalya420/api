import pickle
from abc import ABC
from typing import Union, TypeVar, Callable

from redis.asyncio import Redis

T = TypeVar('T')


class RedisCacheMixin(ABC):
    """
    Mixin for managing Redis caching operations.

    This mixin provides methods for setting, getting, and deleting values
    in a Redis cache. It allows for easy integration of caching functionality
    into classes that require it.

    Attributes:
        _redis (Union[Redis, None]): The Redis instance used for caching.
    """
    _redis: Union[Redis, None] = None

    @classmethod
    def set_redis(cls, instance: Redis):
        """
        Set the Redis instance for the class.

        This method assigns the provided Redis instance to the class-level
        attribute, allowing other methods in the mixin to interact with
        the Redis cache.

        Args:
            instance (Redis): An instance of the Redis client to be used
                              for caching operations.
        """
        cls._redis = instance

    @classmethod
    async def cache_set(cls, key: str, value: bytes, *args, **kwargs) -> None:
        """
        Set a value in the Redis cache.

        This method stores the specified value in the cache under the
        given key. If the Redis instance is not set, the operation is
        ignored.

        Args:
            key (str): The key under which the value will be stored.
            value (bytes): The value to be cached.
            *args: Additional positional arguments to pass to the Redis set method.
            **kwargs: Additional keyword arguments to pass to the Redis set method.
        """
        if cls._redis is not None:
            await cls._redis.set(key, value, *args, **kwargs)

    @classmethod
    async def cache_get(cls, key: str) -> bytes:
        """
        Get a value from the Redis cache.

        This method retrieves the value associated with the given key
        from the cache. If the Redis instance is not set, the operation
        is ignored, and None is returned.

        Args:
            key (str): The key for which the cached value is to be retrieved.

        Returns:
            Union[bytes, None]: The cached value if found, or None if not.
        """
        if cls._redis is not None:
            value = await cls._redis.get(key)
            return value

    @classmethod
    async def cache_delete(cls, key: str) -> None:
        """
        Delete a value from the Redis cache.

        This method removes the value associated with the given key
        from the cache. If the Redis instance is not set, the operation
        is ignored.

        Args:
            key (str): The key of the value to be deleted from the cache.
        """
        if cls._redis is not None:
            await cls._redis.delete(key)

    @classmethod
    async def with_cache(cls, key: str, getter: Callable[..., T], *getter_args, **getter_kwargs) -> Union[T, None]:
        """
        Retrieve a value from the cache or compute it using a getter function.

        This method first attempts to get the value associated with the
        specified key from the cache. If the value is not found, it calls
        the provided getter function with the specified arguments to compute
        the value, caches it, and then returns it.

        Args:
            key (str): The key to look up in the cache.
            getter (Callable[..., T]): A callable that will be invoked to compute
                                        the value if it is not found in the cache.
            *getter_args: Positional arguments to pass to the getter function.
            **getter_kwargs: Keyword arguments to pass to the getter function.

        Returns:
            Union[T, None]: The cached instance if found, or the newly computed
                             instance if not found, or None if no instance is available.
        """
        cached = await cls.cache_get(key)
        if cached:
            return pickle.loads(cached)
        instance = await getter(*getter_args, **getter_kwargs)
        if instance is not None:
            await cls.cache_set(key, pickle.dumps(instance))
        return instance
