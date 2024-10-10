from abc import ABC
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, Union, AsyncGenerator, Self

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class SessionManagementMixin(ABC):
    """
    Mixin for managing database sessions using SQLAlchemy's asynchronous session management.

    This mixin provides methods for creating and managing database sessions
    in an asynchronous context. It allows for session reuse and context
    management, making it easier to work with SQLAlchemy in asynchronous
    applications.

    Attributes:
        session_factory (async_sessionmaker): A factory for creating
                                              asynchronous database sessions.
        context (Dict[Any, Any]): An optional context dictionary for
                                   storing additional information.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker,
        context: Optional[Dict[Any, Any]] = None,
    ):
        """
        Initialize the SessionManagementMixin with a session factory and optional context.

        Args:
            session_factory (async_sessionmaker): A factory for creating
                                                  asynchronous database sessions.
            context (Optional[Dict[Any, Any]]): An optional dictionary for
                                                 storing additional context
                                                 information. Defaults to None.
        """
        self.session_factory: async_sessionmaker = session_factory
        self.context: Dict[Any, Any] = context or dict()
        self._running_session: Union[AsyncSession, None] = None

    def get_running_session(self) -> Union[AsyncSession, None]:
        """
        Retrieve the currently running database session from the context.

        This method checks the context for an existing session and returns it
        if available. If no session is found, it returns None.

        Returns:
            Union[AsyncSession, None]: The currently running session if found,
                                        or None if no session is available.
        """
        return self._running_session

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a database session for the duration of the context.

        This method checks if there is an existing session in the context.
        If so, it reuses that session; otherwise, it creates a new session
        using the session factory. The session is automatically committed
        and closed when the context is exited.

        Yields:
            AsyncSession: An asynchronous database session for use within
                          the context.

        Raises:
            Exception: Any exceptions raised during session management will
                       propagate to the caller.
        """
        if running_session := self.get_running_session():
            yield running_session
        else:
            async with self.session_factory() as session:
                try:
                    self._running_session = session
                    yield session
                except Exception as e:
                    await session.rollback()
                    raise
                else:
                    await session.commit()
                finally:
                    await session.close()

    def with_context(self, context: Dict[Any, Any]) -> Self:
        """
        Create a new instance of the mixin with an updated context.

        This method allows for creating a new instance of the mixin
        with a modified context while retaining the original session factory.

        Args:
            context (Dict[Any, Any]): A dictionary containing the new context
                                       information.

        Returns:
            Self: A new instance of the mixin with the updated context.
        """
        return self.__class__(
            session_factory=self.session_factory, context={**self.context, **context}
        )

    def reuse_session(self):
        if self._running_session is None:
            raise RuntimeError("No running database session")
        return self.with_context({**self.context, "session": self._running_session})
