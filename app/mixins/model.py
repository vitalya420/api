import datetime
from sqlalchemy import Column, Integer, DateTime
from app.db import Base
from app.mixins.cacheable import CacheableMixin


class CacheableModelMixin(Base, CacheableMixin):
    """
    An abstract mixin class that provides common fields and caching capabilities for SQLAlchemy models.

    This class serves as a base for other models, providing common attributes such as
    `id`, `created_at`, and `updated_at`. It also implements the `get_key` method
    from the `CacheableMixin` to generate a unique cache key for each instance.
    """

    __abstract__ = True  # This class will not be mapped to a table

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The primary key of the model.

    This field is an auto-incrementing integer that uniquely identifies each record in the database.
    """

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    """
    The timestamp when the record was created.

    This field is automatically set to the current UTC time when a new record is created.
    """

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    """
    The timestamp when the record was last updated.

    This field is automatically set to the current UTC time when the record is created and
    updated each time the record is modified.
    """

    def get_key(self) -> str:
        """
        Generate a unique cache key for the model instance.

        This method constructs a cache key using the table name and the instance's primary key.

        Returns:
            str: A unique cache key in the format '{tablename}:{id}'.
        """
        return f'{self.__tablename__}:{self.id}'

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
        return f'{cls.__tablename__}:{key}'
