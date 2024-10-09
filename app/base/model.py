import datetime

from sqlalchemy import Column, Integer, DateTime

from app.db import Base
from app.mixins import CacheableMixin


class BaseModelWithID(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class BaseModelWithDateTimeFields(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # noqa
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,  # noqa
        onupdate=datetime.datetime.utcnow,  # noqa
    )


class BaseModelWithIDAndDateTimeFields(BaseModelWithID, BaseModelWithDateTimeFields):
    __abstract__ = True


class BaseCachableModel(Base, CacheableMixin):
    __abstract__ = True
    __cache_key_attr__ = None

    def get_key(self) -> str:
        if self.__cache_key_attr__ is None:
            raise NotImplementedError(
                "__cache_key_attr__ is not set. Set or override get_key(self)"
            )
        value = getattr(self, self.__cache_key_attr__)
        return f"{self.__tablename__}:{value}"

    @classmethod
    def lookup_key(cls, key: str) -> str:
        return f"{cls.__tablename__}:{key}"


class BaseCachableModelWithID(BaseCachableModel, BaseModelWithID):
    __abstract__ = True
    __cache_key_attr__ = "id"


class BaseCachableModelWithIDAndDateTimeFields(
    BaseCachableModelWithID, BaseModelWithIDAndDateTimeFields
):
    __abstract__ = True


__all__ = [
    "BaseModelWithID",
    "BaseModelWithDateTimeFields",
    "BaseModelWithIDAndDateTimeFields",
    "BaseCachableModel",
    "BaseCachableModelWithID",
    "BaseCachableModelWithIDAndDateTimeFields",
]
