from typing import Type, Any, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.base import BaseService
from app.utils.misc.registry import Registry


class ServiceFactory:
    """
    A factory class for creating service instances on demand (lazy instantiation).

    This class is designed to manage the lifecycle of service instances, ensuring that
    each service is only created when it is accessed for the first time. It utilizes
    a session factory for database interactions and a registry to manage service
    classes.

    Attributes:
        session_factory (async_sessionmaker): An asynchronous session factory used
            to create database sessions for the services.
        services (Registry[Type[BaseService]]): A registry that maps service names
            to their corresponding service classes.
        context (dict[Any, Any]): A dictionary that contains useful information
            to be passed to the service instances, allowing for additional context
            during service initialization.
        _instances (dict[str, BaseService]): A private dictionary that caches
            created service instances to avoid redundant instantiation.

    Methods:
        get_or_create(service: str) -> BaseService:
            Retrieves an existing service instance if it exists; otherwise, it
            creates a new instance, caches it, and returns it.

        __getattr__(service: str) -> BaseService:
            Allows for attribute-style access to retrieve service instances by name.
            This method delegates to `get_or_create` to ensure lazy instantiation.

    Usage:
        service_factory = ServiceFactory(session_factory, services_registry, context={'key': 'value'})

        # Access a service instance
        user_service = service_factory.get_or_create('user_service')

        # Alternatively, using attribute-style access
        user_service = service_factory.user_service
    """

    def __init__(self,
                 session_factory: async_sessionmaker,
                 services: Registry[Type[BaseService]],
                 context: Optional[dict[Any, Any]] = None) -> None:
        self.session_factory: async_sessionmaker = session_factory
        self.services: Registry[Type[BaseService]] = services
        self.context: dict[Any, Any] = context or dict()
        self._instances: dict[str, BaseService] = {}

    def get_or_create(self, service: str) -> BaseService:
        if service in self._instances:
            return self._instances[service]
        instance = self.services[service](self.session_factory, self.context)
        self._instances[service] = instance
        return instance

    def __getattr__(self, service: str) -> BaseService:
        return self.get_or_create(service)
