from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.db import async_session_factory
from app.models import User
from .base import BaseService


class UserService(BaseService):
    async def get(self, phone: str):
        async with self.session_factory() as session:
            return self._get_user(session, phone)

    async def get_by_id(self, user_id: int):
        query = select(User).where(User.id == user_id)
        async with self.session_factory() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def create(self, phone: str):
        async with self.get_session() as session:
            instance = User(phone=phone)
            session.add(instance)

    async def get_or_create(self, phone: str):
        async with self.get_session() as session:
            existing_user = await self._get_user(session, phone)
            if existing_user:
                return existing_user
            await self.with_context({'session': session}).create(phone)
            return await self._get_user(session, phone)

    @staticmethod
    async def _get_user(session: AsyncSession, phone: str):
        query = select(User).where(eq(User.phone, phone))
        result = await session.execute(query)
        return result.scalars().first()


user_service = UserService(async_session_factory)
