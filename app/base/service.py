from contextlib import asynccontextmanager
from typing import Type, Union, TypeVar, List

from redis.asyncio import Redis

from app.base.repository import BaseRepository

from app.mixins import SessionManagementMixin, RedisCacheMixin

T = TypeVar("T", bound=BaseRepository)


class BaseService(RedisCacheMixin, SessionManagementMixin):
    _redis: Union[Redis, None] = None
    __repository_class__: Union[Type[BaseRepository], None] = None

    @classmethod
    def set_redis(cls, instance: Redis) -> None:
        # Set redis instance only for BaseService and its children
        # but not for RedisCacheMixin children
        cls._redis = instance

    @asynccontextmanager
    async def get_repo(self, *repo_or_repos: Type[T]) -> Union[T, List[T]]:
        async with self.get_session() as session:
            # If there are no repo classes provided create instance
            # of __repository_class__
            if len(repo_or_repos) == 0:
                if self.__repository_class__ is None:
                    raise RuntimeError("No repository class or classes proved")
                yield self.__repository_class__(session)
            # If there is only one repo class provided then
            # yield single instance
            elif len(repo_or_repos) == 1:
                yield repo_or_repos[0](session)
            # Else create and return instances for all classes
            else:
                yield [repo(session) for repo in repo_or_repos]
