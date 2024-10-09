from abc import ABC
from typing import Union, Callable, Type, Awaitable

from redis.asyncio import Redis

from app.mixins.cacheable import CacheableMixin


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
    async def cache_object(cls, object_: CacheableMixin) -> None:
        """
        Cache a cacheable object in Redis.

        This method takes an instance of a class that implements the
        `CacheableMixin` and stores it in the Redis cache. The object's
        unique cache key is generated using the `get_key` method from
        the `CacheableMixin`, and the object is serialized to bytes
        before being stored.

        Args:
            object_ (CacheableMixin): An instance of a class that implements
                                       the `CacheableMixin`. This object
                                       must have a `get_key` method and
                                       should be serializable using the
                                       `pickle` module.

        Raises:
            TypeError: If the provided object does not implement the
                        `CacheableMixin` interface.
        """
        await cls.cache_set(object_.get_key(), bytes(object_))

    @classmethod
    async def cache_delete_object(cls, object_: CacheableMixin) -> None:
        """
        Delete a cacheable object from Redis.

        This method removes the cached representation of an object that
        implements the `CacheableMixin` from the Redis cache. The object's
        unique cache key is generated using the `get_key` method from
        the `CacheableMixin`.

        Args:
            object_ (CacheableMixin): An instance of a class that implements
                                       the `CacheableMixin`. This object
                                       must have a `get_key` method.

        Raises:
            TypeError: If the provided object does not implement the
                        `CacheableMixin` interface.
        """
        await cls.cache_delete(object_.get_key())

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
    async def with_cache(
        cls,
        class_: Type[CacheableMixin],
        key: Union[str, int],
        getter: Callable[..., Awaitable[CacheableMixin]],
        *getter_args,
        **getter_kwargs
    ) -> Union[CacheableMixin, None]:
        """
        Retrieve a value from the cache or compute it using a getter function.

        This method first attempts to get the value associated with the
        specified key from the cache. If the value is not found, it calls
        the provided getter function with the specified arguments to compute
        the value, caches it, and then returns it.

        Args:
            class_ (Type[CacheableMixin]): The class type of the cacheable object.
                                            This class must implement the `CacheableMixin`
                                            interface and provide a `lookup_key` method.
            key (Union[str, int]): The primary key or unique identifier to look up
                                  in the cache. This value is used to generate
                                  the lookup cache key.
            getter (Callable[..., Awaitable[CacheableMixin]]): An asynchronous callable
                                                                that will be invoked to compute
                                                                the value if it is not found in the cache.
            *getter_args: Positional arguments to pass to the getter function.
            **getter_kwargs: Keyword arguments to pass to the getter function.

        Returns:
            Union[CacheableMixin, None]: The cached instance if found, or the newly computed
                                          instance if not found, or None if no instance is available.
        """
        lookup_key = class_.lookup_key(key)
        cached = await cls.cache_get(lookup_key)
        if cached:
            return class_.from_bytes(cached)
        instance: Union[CacheableMixin, None] = await getter(
            *getter_args, **getter_kwargs
        )
        if instance is not None:
            await cls.cache_set(
                instance.get_key(), bytes(instance), ex=60 * 60
            )  # TODO: No magic numbers
        return instance
