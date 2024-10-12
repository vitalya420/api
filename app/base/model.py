import datetime
from typing import Union, List

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import Mapped

from app.db import Base
from app.mixins import CacheableMixin


class BaseModelWithID(Base):
    """
    Abstract base model class with an auto-incrementing ID.

    This class provides a primary key field `id` for models that inherit from it.
    It is intended to be used as a base class for other models that require a unique
    identifier.

    Attributes:
        id (int): The unique identifier for the model, automatically generated.
    """

    __abstract__ = True

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)


class BaseModelWithDateTimeFields(Base):
    """
    Abstract base model class with created and updated timestamp fields.

    This class provides `created_at` and `updated_at` fields for models that inherit
    from it. These fields automatically track the creation and last update times of
    the model instances.

    Attributes:
        created_at (datetime): The timestamp when the model instance was created.
        updated_at (datetime): The timestamp when the model instance was last updated.
    """

    __abstract__ = True

    created_at: Mapped[datetime.datetime] = Column(
        DateTime, default=datetime.datetime.utcnow
    )  # noqa
    updated_at: Mapped[datetime.datetime] = Column(
        DateTime,
        default=datetime.datetime.utcnow,  # noqa
        onupdate=datetime.datetime.utcnow,  # noqa
    )


class BaseModelWithIDAndDateTimeFields(BaseModelWithID, BaseModelWithDateTimeFields):
    """
    Abstract base model class with an ID and timestamp fields.

    This class combines the functionality of `BaseModelWithID` and
    `BaseModelWithDateTimeFields`, providing both an auto-incrementing ID
    and timestamp fields for tracking creation and update times.
    """

    __abstract__ = True


class BaseCachableModel(Base, CacheableMixin):
    """
    Abstract base model class with caching capabilities.

    This class provides caching functionality for models that inherit from it.
    It includes methods for generating cache keys based on unique attributes
    and managing reference keys for cached data.

    Attributes:
        __cache_key_attr__ (Union[str, List[str], None]): The attribute(s) used to
            generate the cache key.
            There should be a unique field or a list of fields.
    """

    __abstract__ = True
    __cache_key_attr__: Union[str, List[str], None] = None

    def get_key(self) -> str:
        """
        Generate the cache key for the model instance.

        Returns:
            str: The generated cache key.

        Raises:
            NotImplementedError: If __cache_key_attr__ is not set.
        """
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
        """
        Generate reference keys for the model instance.

        Returns:
            List[str]: A list of reference keys based on additional attributes
                        defined in __cache_key_attr__.
        """
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
        """
        Generate a lookup key for the class.

        Args:
            key (str): The key to be looked up.

        Returns:
            str: The formatted lookup key.
        """
        return f"{cls.__tablename__}:{key}"

    @classmethod
    def lookup_reference_keys(cls, key: str) -> List[str]:
        """
        Generate reference lookup keys for the class.

        Args:
            key (str): The key to be looked up.

        Returns:
            List[str]: A list of reference keys for the class.
        """
        if isinstance(cls.__cache_key_attr__, List) and len(cls.__cache_key_attr__) > 1:
            ref_keys = [
                f"ref:{cls.__tablename__}:{attr_}:{key}"
                for attr_ in cls.__cache_key_attr__[1:]
            ]
            return ref_keys


class BaseCachableModelWithID(BaseCachableModel, BaseModelWithID):
    """
    Abstract base model class with caching capabilities and an ID.

    This class combines the functionality of `BaseCachableModel` and
    `BaseModelWithID`, providing caching capabilities along with an
    auto-incrementing ID field.

    Attributes:
        __cache_key_attr__ (str): The attribute used to generate the cache key,
                                   set to "id".
    """

    __abstract__ = True
    __cache_key_attr__ = "id"


class BaseCachableModelWithIDAndDateTimeFields(
    BaseCachableModelWithID, BaseModelWithIDAndDateTimeFields
):
    """
    Abstract base model class with caching capabilities, an ID, and timestamp fields.

    This class combines the functionality of `BaseCachableModelWithID` and
    `BaseModelWithIDAndDateTimeFields`, providing caching capabilities,
    an auto-incrementing ID, and fields for tracking creation and update times.
    """

    __abstract__ = True


__all__ = [
    "BaseModelWithID",
    "BaseModelWithDateTimeFields",
    "BaseModelWithIDAndDateTimeFields",
    "BaseCachableModel",
    "BaseCachableModelWithID",
    "BaseCachableModelWithIDAndDateTimeFields",
]
