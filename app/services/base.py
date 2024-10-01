from abc import ABC
from contextlib import asynccontextmanager
from typing import Optional, Any, Self, AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class BaseService(ABC):
    """
    Base service class for managing database sessions.

    This class provides a foundation for services that require
    interaction with a database using SQLAlchemy's asynchronous
    session management. It allows for session reuse and context
    management.

    Attributes:
        session_factory (async_sessionmaker): A factory for creating
                                              asynchronous database sessions.
        context (dict[Any, Any]): An optional context dictionary for
                                  storing additional information.
    """

    def __init__(self,
                 session_factory: async_sessionmaker,
                 context: Optional[dict[Any, Any]] = None) -> None:
        """
        Initialize the BaseService with a session factory and optional context.

        Args:
            session_factory (async_sessionmaker): A factory for creating
                                                  asynchronous database sessions.
            context (Optional[dict[Any, Any]]): An optional dictionary for
                                                 storing additional context
                                                 information. Defaults to None.
        """
        self.session_factory: async_sessionmaker = session_factory
        self.context: dict[Any, Any] = context or dict()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a database session for the duration of the context.

        This method checks if there is an existing session in the context.
        If so, it reuses that session; otherwise, it creates a new session
        using the session factory. The session is automatically closed
        when the context is exited.

        Yields:
            AsyncSession: An asynchronous database session for use within
                          the context.

        Raises:
            Exception: Any exceptions raised during session management will
                       propagate to the caller.
        """
        running_session = self.context.get('session')
        if running_session:
            yield running_session
        else:
            async with self.session_factory() as session:
                try:
                    yield session
                finally:
                    await session.commit()
                    await session.close()

    def with_context(self, context: dict) -> Self:
        """
        Create a new instance of the service with an updated context.

        This method allows for creating a new instance of the service
        with a modified context while retaining the original session factory.

        Args:
            context (dict): A dictionary containing the new context
                            information.

        Returns:
            Self: A new instance of the service with the updated context.
        """
        return self.__class__(session_factory=self.session_factory, context=context)
