from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.models import User
from .base import BaseService
from ..db import async_session_factory


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
        async with self.session_factory() as session:
            async with session.begin():
                instance = User(phone=phone)
                session.add(instance)
            await session.refresh(instance)
            return instance

    async def get_or_create(self, phone: str):
        """Runs in single session"""
        async with self.session_factory() as session:
            user = await self._get_user(session, phone)

            if not user:
                user = User(phone=phone)
                session.add(user)
                await session.commit()
                await session.refresh(user)

            return user

    @staticmethod
    async def _get_user(session: AsyncSession, phone: str):
        query = select(User).where(eq(User.phone, phone))
        result = await session.execute(query)
        return result.scalars().first()


user = UserService(async_session_factory)
