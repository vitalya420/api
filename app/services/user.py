import pickle
from typing import Union, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.db import async_session_factory
from app.models import User
from .base import BaseService


class UserService(BaseService):
    async def get_user_by_phone(self, phone: str) -> Union[User, None]:
        async with self.get_session() as session:
            user = await self._get_user(phone, session)
            await self.cache_object(user)
            return user

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        query = select(User).where(User.id == user_id)
        async with self.get_session() as session:
            result = await session.execute(query)
            user = result.scalars().first()
            await self.cache_object(user)
            return user

    async def create(self, phone: str) -> User:
        async with self.get_session() as session:
            instance = User(phone=phone)
            session.add(instance)
        return instance

    async def get_or_create(self, phone: str):
        async with self.get_session() as session:
            existing_user = await self._get_user(phone, session)
            if existing_user:
                await self.cache_object(existing_user)
                return existing_user
            await self.with_context({'session': session}).create(phone)
            user = await self._get_user(phone, session)
        await self.cache_object(user)
        return user

    @staticmethod
    async def _get_user(phone: str, session: AsyncSession):
        query = select(User).where(eq(User.phone, phone))
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_by_id_with_cache(self, user_id: int) -> Union[User, None]:
        return await self.with_cache(
            User, user_id,
            self.get_user_by_id, user_id
        )


user_service = UserService(async_session_factory)
