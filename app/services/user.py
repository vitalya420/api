from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.models import User
from app.services import services
from app.services.base import BaseService


@services("user")
class UserService(BaseService):
    async def get(self, phone: str):
        async with self.session_factory() as session:
            return self._get_user(session, phone)

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

