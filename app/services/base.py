from abc import ABC

from sqlalchemy.ext.asyncio import async_sessionmaker


class BaseService(ABC):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory: async_sessionmaker = session_factory
