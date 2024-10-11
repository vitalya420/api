from abc import ABC
from typing import Union, Callable, Type, Awaitable, List

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
    async def cache_set(
        cls, key: str, value: Union[bytes, str], *args, **kwargs
    ) -> None:
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
    async def cache_get(cls, key: Union[str, bytes]) -> bytes:
        """
        Get a value from the Redis cache.

        This method retrieves the value associated with the given key
        from the cache. If the Redis instance is not set, the operation
        is ignored, and None is returned.

        Args:
            key (Union[str, bytes]): The key for which the cached value is to be retrieved.

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
        await cls.cache_instance(object_)

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
        **getter_kwargs,
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
        if result := await cls.get_instance_from_cache_by_key(lookup_key, class_):
            return result

        ref_keys = class_.lookup_reference_keys(key)
        main_key = await cls.search_main_key(ref_keys) if ref_keys else None
        if main_key and (
            result := await cls.get_instance_from_cache_by_key(main_key, class_)
        ):
            return result

        instance: Union[CacheableMixin, None] = await getter(
            *getter_args, **getter_kwargs
        )
        if instance is not None:
            await cls.cache_instance(instance)
        return instance

    @classmethod
    async def get_instance_from_cache_by_key(
        cls, key: Union[str, bytes], class_: Type[CacheableMixin]
    ) -> Union[CacheableMixin, None]:
        """
        Retrieve an instance from the cache using the specified key.

        This method attempts to get a cached instance associated with the provided key.
        If a cached instance is found, it is deserialized from bytes into an instance of
        the specified class.

        Args:
            cls: The class method context.
            key (Union[str, bytes]): The cache key used to look up the instance.
            class_ (Type[CacheableMixin]): The class type of the cacheable object.

        Returns:
            Union[CacheableMixin, None]: The deserialized instance if found, or None if not found.
        """
        cached = await cls.cache_get(key)
        if cached:
            return class_.from_bytes(cached)

    @classmethod
    async def search_main_key(cls, reference_keys: List[str]) -> Union[bytes, None]:
        """
        Search for the main key in the cache using a list of reference keys.

        This method iterates through the provided reference keys and attempts to retrieve
        a cached instance. The first cached instance found is returned.

        Args:
            cls: The class method context.
            reference_keys (List[str]): A list of reference keys to search in the cache.

        Returns:
            Union[bytes, None]: The cached value if found, or None if not found.
        """
        for reference_key in reference_keys:
            cached = await cls.cache_get(reference_key)
            if cached:
                return cached

    @classmethod
    async def cache_instance(cls, instance: CacheableMixin, ex=60 * 60):
        """
        Cache an instance and its reference keys.

        This method stores the provided instance in the cache using its main key.
        It also caches any reference keys associated with the instance.

        Args:
            cls: The class method context.
            instance (CacheableMixin): The instance to be cached.
            ex (int, optional): The expiration time for the cache in seconds. Defaults to 3600 seconds (1 hour).
        """
        main_key = instance.get_key()
        await cls.cache_set(main_key, bytes(instance), ex=ex)
        ref_keys = instance.get_reference_keys()
        for ref in ref_keys:
            await cls.cache_set(ref, main_key, ex=ex)
