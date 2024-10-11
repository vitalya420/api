from contextlib import asynccontextmanager
from typing import Type, Union, TypeVar, List, AsyncGenerator

from redis.asyncio import Redis

from app.base.repository import BaseRepository
from app.mixins import SessionManagementMixin, RedisCacheMixin

T = TypeVar("T", bound=BaseRepository)


class BaseService(RedisCacheMixin, SessionManagementMixin):
    """
    Base service class for managing repositories with Redis caching and session management.

    This class provides a foundation for service classes that require access to
    repositories and Redis for caching. It includes methods for setting a Redis
    instance and obtaining repository instances with an active session.

    Attributes:
        _redis (Union[Redis, None]): The Redis instance used for caching.
        __repository_class__ (Union[Type[BaseRepository], None]): The default repository
            class to be used if no specific repository classes are provided.
    """

    _redis: Union[Redis, None] = None
    __repository_class__: Union[Type[BaseRepository], None] = None

    @classmethod
    def set_redis(cls, instance: Redis) -> None:
        """
        Set the Redis instance for the service class and its subclasses.

        This method allows the assignment of a Redis instance to be used for caching
        within the service and its derived classes, while preventing assignment
        for classes that inherit from `RedisCacheMixin`.

        Args:
            instance (Redis): An instance of the Redis client to be used for caching.
        """
        cls._redis = instance

    @asynccontextmanager
    async def get_repo(
        self, *repo_or_repos: Type[T]
    ) -> AsyncGenerator[Union[T, List[T]], None]:
        """
        Asynchronously obtain repository instances with an active session.

        This method provides a context manager that yields repository instances
        based on the provided repository classes. It ensures that an active session
        is available for the repositories.

        Args:
            *repo_or_repos (Type[T]): One or more repository classes to instantiate.

        Yields:
            AsyncGenerator[Union[T, List[T]], None]: A single repository instance if
            one class is provided, or a list of repository instances if multiple
            classes are provided. If no classes are provided, it yields an instance
            of the default repository class defined in __repository_class__.

        Raises:
            RuntimeError: If no repository class or classes are provided and
            __repository_class__ is not set.
        """
        async with self.get_session() as session:
            # If there are no repo classes provided, create instance
            # of __repository_class__
            if len(repo_or_repos) == 0:
                if self.__repository_class__ is None:
                    raise RuntimeError("No repository class or classes provided")
                yield self.__repository_class__(session)
            # If there is only one repo class provided then
            # yield single instance
            elif len(repo_or_repos) == 1:
                yield repo_or_repos[0](session)
            # Else create and return instances for all classes
            else:
                yield [repo(session) for repo in repo_or_repos]
