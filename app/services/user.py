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
            return await self._cache(user)

    async def get_user_by_id(self, user_id: int) -> Union[User, None]:
        query = select(User).where(User.id == user_id)
        async with self.get_session() as session:
            result = await session.execute(query)
            user = result.scalars().first()
            return await self._cache(user)

    async def create(self, phone: str):
        async with self.get_session() as session:
            instance = User(phone=phone)
            session.add(instance)

    async def get_or_create(self, phone: str):
        async with self.get_session() as session:
            existing_user = await self._get_user(phone, session)
            if existing_user:
                return await self._cache(existing_user)
            await self.with_context({'session': session}).create(phone)
            return await self._cache(await self._get_user(phone, session))

    @staticmethod
    async def _get_user(phone: str, session: AsyncSession):
        query = select(User).where(eq(User.phone, phone))
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_by_id_with_cache(self, id_: int):
        key = f"user:{id_}"
        user = await self.with_cache(
            key, self.get_user_by_id, id_,
        )
        return user

    async def _cache(self, user: Optional[User]) -> Union[User, None]:
        """Helper method to save user in cache and return this user"""
        if user is None:
            return None
        await self.save_user_in_cache(user)
        return user

    async def save_user_in_cache(self, user: User):
        await self.cache_set(f"user:{user.id}", pickle.dumps(user))

    async def remove_user_from_cache(self, user: User):
        await self.cache_delete(f"user:{user.id}")


user_service = UserService(async_session_factory)
