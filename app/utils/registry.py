from typing import TypeVar, Union

T = TypeVar('T')


class Registry(dict[str, T]):
    """
    A generic registry class that allows for the registration and retrieval of classes
    or instances by name. This is particularly useful for avoiding circular imports
    in larger applications.

    The Registry can be used to register classes or instances with a string key,
    and it provides a convenient way to retrieve them later.

    Usage:
        - To register a class or instance, you can either use a decorator or call
          the registry directly with a class.

        Example:
            registry = Registry()

            @registry('my_class')
            class MyClass:
                pass

            # or directly
            class AnotherClass:
                pass

            registry(AnotherClass)

            # Retrieve the registered classes
            my_class_instance = registry['my_class']()  # Create an instance of MyClass
            another_class_instance = registry['anotherclass']()  # Create an instance of AnotherClass

    Attributes:
        - __call__(name_or_cls: Union[T, str]):
            If a string is provided, it returns a decorator that registers the class
            with that name. If a class is provided, it registers the class using its
            lowercase name as the key.

        - __getattr__(name: str) -> T:
            Allows for attribute-style access to retrieve registered classes by name.
            For example, `registry.my_class` will return the class registered under
            the name 'my_class'.

    Example:
        registry = Registry()

        @registry('example_class')
        class ExampleClass:
            pass

        instance = registry['example_class']()  # Create an instance of ExampleClass
    """

    def __call__(self, name_or_cls: Union[T, str]):
        if isinstance(name_or_cls, str):
            def wrapper(cls: T):
                self[name_or_cls] = cls

            return wrapper
        else:
            self[name_or_cls.__name__.lower()] = name_or_cls

    def __getattr__(self, name: str) -> T:
        return self[name]
