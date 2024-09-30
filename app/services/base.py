from abc import ABC
from typing import Optional, Any

from sqlalchemy.ext.asyncio import async_sessionmaker


class BaseService(ABC):
    def __init__(self,
                 session_factory: async_sessionmaker,
                 context: Optional[dict[Any, Any]] = None) -> None:
        self.session_factory: async_sessionmaker = session_factory
        self.context: dict[Any, Any] = context
