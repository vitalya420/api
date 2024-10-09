from contextlib import contextmanager, asynccontextmanager
from typing import Type, Union, List, TypeVar

from redis.asyncio import Redis

from app.mixins.cache import RedisCacheMixin
from app.mixins.session import SessionManagementMixin
from app.repositories.base import BaseRepository

T = TypeVar("T", bound=BaseRepository)


class BaseService(RedisCacheMixin, SessionManagementMixin):
    """
    Base service class that combines Redis caching and database session management.

    This class serves as a foundation for services that require both
    caching functionality using Redis and database interaction using
    SQLAlchemy's asynchronous session management. It allows for easy
    integration of both caching and session management in a single
    service.

    Attributes:
        _redis (Union[Redis, None]): The Redis instance used for caching.
    """

    _redis = None
    __repository_class__: Type[BaseRepository]

    @classmethod
    def set_redis(cls, instance: Redis):
        """
        Set the Redis instance for the class.

        This method overloads the `set_redis` method from the
        `RedisCacheMixin` to assign the provided Redis instance to
        the class-level attribute, allowing other methods in the
        mixin to interact with the Redis cache.

        Args:
            instance (Redis): An instance of the Redis client to be used
                              for caching operations.
        """
        cls._redis = instance

    @asynccontextmanager
    async def get_repo(self, *repos: Type[T]) -> Union[T, List[T]]:
        async with self.get_session() as session:  # yields new async session
            if len(repos) == 0 and self.__repository_class__ is not None:
                yield self.__repository_class__(session)
            elif len(repos) > 1:
                yield [repo(session) for repo in repos]
            else:
                yield repos[0](session)
