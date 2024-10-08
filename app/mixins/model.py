import datetime

from sqlalchemy import Column, Integer, DateTime

from app.db import Base
from app.mixins.cacheable import CacheableMixin


class CachableModelNoFieldsMixin(Base, CacheableMixin):
    """
    An abstract mixin class that provides a base for cacheable SQLAlchemy models.

    This class defines the structure for cacheable models, including methods for
    generating cache keys. It requires subclasses to define a primary key.

    Attributes:
        __primary_key__ (str): The name of the primary key attribute for the model.
    """

    __abstract__ = True
    __primary_key__ = None

    @classmethod
    def lookup_key(cls, key: str) -> str:
        """
        Generate a lookup cache key for the model instance.

        This method constructs a cache key using the table name and a provided key.
        It is useful for generating keys for specific attributes or related data
        associated with the model instance.

        Args:
            key (str): The specific key or identifier to be included in the cache key.

        Returns:
            str: A lookup cache key in the format '{tablename}:{key}'.
        """
        return f"{cls.__tablename__}:{key}"

    def get_key(self) -> str:
        """
        Generate a unique cache key for the model instance based on the primary key.

        This method retrieves the value of the primary key attribute and constructs
        a cache key in the format '{tablename}:{primary_key_value}'.

        Raises:
            NotImplementedError: If the primary key is not defined for the model.

        Returns:
            str: A unique cache key for the model instance.
        """
        if self.__primary_key__ is None:
            raise NotImplementedError("Primary key is not defined.")
        value = getattr(self, self.__primary_key__)
        return f"{self.__tablename__}:{value}"


class CachableModelWithIDMixin(CachableModelNoFieldsMixin):
    """
    A mixin class that adds a default integer primary key field to cacheable models.

    This class defines a primary key field named 'id' for use in subclasses.

    Attributes:
        __primary_key__ (str): The name of the primary key attribute for the model.
        id (Column): The primary key column of type Integer.
    """

    __abstract__ = True
    __primary_key__ = "id"

    id = Column(Integer, primary_key=True, autoincrement=True)


class CachableModelWithDateTimeFieldsMixin(CachableModelWithIDMixin):
    """
    An abstract mixin class that provides common fields and caching capabilities for SQLAlchemy models.

    This class serves as a base for other models, providing common attributes such as
    `id`, `created_at`, and `updated_at`. It also implements the `get_key` method
    from the `CacheableMixin` to generate a unique cache key for each instance.

    Attributes:
        created_at (DateTime): The timestamp when the record was created.
        updated_at (DateTime): The timestamp when the record was last updated.
    """

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    """
    The timestamp when the record was created.

    This field is automatically set to the current UTC time when a new record is created.
    """

    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    """
    The timestamp when the record was last updated.

    This field is automatically set to the current UTC time when the record is created and
    updated each time the record is modified.
    """
