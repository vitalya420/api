import datetime
from typing import Union, List

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
    # Cache key attribute should be unique field to create key in storage
    # If there will be more than one key - first key will be real value
    # other - references to first key
    # for example users:1 - <real user value>
    # then ref:users:phone:+11111111 - will be reference to users:1

    __cache_key_attr__: Union[str, List[str], None] = None

    def get_key(self) -> str:
        if self.__cache_key_attr__ is None:
            raise NotImplementedError(
                "__cache_key_attr__ is not set. Set or override get_key(self)"
            )
        if isinstance(self.__cache_key_attr__, str):
            value = getattr(self, self.__cache_key_attr__)
            return f"{self.__tablename__}:{value}"
        elif (
            isinstance(self.__cache_key_attr__, List)
            and len(self.__cache_key_attr__) > 0
        ):
            return f"{self.__tablename__}:{getattr(self, self.__cache_key_attr__[0])}"

    def get_reference_keys(self) -> List[str]:
        if not (
            isinstance(self.__cache_key_attr__, List)
            and len(self.__cache_key_attr__) > 1
        ):
            return list()
        return [
            f"ref:{self.__tablename__}:{attr_}:{getattr(self, attr_)}"
            for attr_ in self.__cache_key_attr__[1:]
        ]

    @classmethod
    def lookup_key(cls, key: str) -> str:
        return f"{cls.__tablename__}:{key}"

    @classmethod
    def lookup_reference_keys(cls, key: str) -> List[str]:
        if isinstance(cls.__cache_key_attr__, List) and len(cls.__cache_key_attr__) > 1:
            ref_keys = [
                f"ref:{cls.__tablename__}:{attr_}:{key}"
                for attr_ in cls.__cache_key_attr__[1:]
            ]
            return ref_keys

    def is_reference_attribute(self, key: str) -> bool:
        if isinstance(self.__cache_key_attr__, List):
            return key in self.__cache_key_attr__[1:]
        return False

    def is_main_attribute(self, key: str) -> bool:
        if isinstance(self.__cache_key_attr__, List):
            return key == self.__cache_key_attr__[0]
        return key == self.__cache_key_attr__


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
