import pickle
from abc import abstractmethod
from typing import Self, List


class CacheableMixin(object):
    """
    A mixin class that provides caching capabilities for objects.

    This mixin is designed to be inherited by classes that require caching functionality.
    Subclasses must implement specific methods to define how caching keys are generated
    and how instances are looked up in the cache.
    """

    @abstractmethod
    def get_key(self) -> str:
        """
        Retrieve a unique key for the cacheable object.

        This method must be implemented by subclasses to return a
        string that uniquely identifies the object in the cache.

        Returns:
            str: A unique key for the cacheable object.
        """
        pass

    def get_reference_keys(self) -> List[str]:
        """
        Retrieve keys that should be referred to the main key (get_key()).

        This method can be overridden by subclasses to provide additional
        keys that are related to the main cache key.

        Returns:
            List[str]: A list of reference keys associated with the cacheable object.
        """
        return list()

    @classmethod
    @abstractmethod
    def lookup_key(cls, key: str) -> str:
        """
        Generate a lookup cache key for the cacheable object.

        This method constructs a cache key using a provided key and
        the unique identifier of the cacheable object. It is useful
        for generating keys for specific attributes or related data
        associated with the object.

        Args:
            key (str): The specific key or identifier to be included
                       in the cache key.

        Returns:
            str: A lookup cache key in the format '{unique_identifier}:{key}'.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        pass

    @classmethod
    def lookup_reference_keys(cls, key: str) -> List[str]:
        """
        Generate a list of reference keys for the cacheable object.

        This method can be overridden by subclasses to provide a list
        of keys that are related to the main cache key.

        Args:
            key (str): The main key for which reference keys are to be generated.

        Returns:
            List[str]: A list of reference keys associated with the provided key.
        """
        return list()

    def to_bytes(self) -> bytes:
        """
        Serialize the object to bytes.

        This method uses the `pickle` module to convert the object
        into a byte representation, which can be stored in a cache.

        Returns:
            bytes: The byte representation of the object.
        """
        return pickle.dumps(self)

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        """
        Deserialize an object from bytes.

        This class method uses the `pickle` module to convert a byte
        representation back into an instance of the class.

        Args:
            data (bytes): The byte representation of the object.

        Returns:
            Self: An instance of the class created from the byte data.
        """
        return pickle.loads(data)

    def __bytes__(self) -> bytes:
        """
        Return the byte representation of the object.

        This method allows the object to be converted to bytes using
        the built-in `bytes()` function, which internally calls the
        `to_bytes()` method.

        Returns:
            bytes: The byte representation of the object.
        """
        return self.to_bytes()
