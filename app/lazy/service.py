from typing import Type

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services import BaseService
from app.utils.registry import Registry


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
        service_factory = ServiceFactory(session_factory, services_registry)

        # Access a service instance
        user_service = service_factory.get_or_create('user_service')

        # Alternatively, using attribute-style access
        user_service = service_factory.user_service
    """

    def __init__(self, session_factory: async_sessionmaker, services: Registry[Type[BaseService]]):
        self.session_factory: async_sessionmaker = session_factory
        self.services: Registry[Type[BaseService]] = services
        self._instances: dict[str, BaseService] = {}

    def get_or_create(self, service: str) -> BaseService:
        if service in self._instances:
            return self._instances[service]
        instance = self.services[service](self.session_factory)
        self._instances[service] = instance
        return instance

    def __getattr__(self, service: str) -> BaseService:
        return self.get_or_create(service)
