from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """
    A base repository class for managing database operations.

    This class serves as a foundation for repository classes that interact
    with a database using SQLAlchemy's asynchronous session. It provides
    a way to encapsulate database operations and manage the session lifecycle.

    Attributes:
        session (AsyncSession): An instance of SQLAlchemy's AsyncSession
                                used for database operations.
    """

    def __init__(self, session: "AsyncSession"):
        """
        Initialize the BaseRepository with a database session.

        Args:
            session (AsyncSession): An instance of AsyncSession that will be
                                    used for executing database operations.
        """
        self.session: "AsyncSession" = session
