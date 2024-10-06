import pickle

from sanic import BadRequest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_factory
from app.models import Business
from .base import BaseService


class BusinessService(BaseService):
    async def create_business(self, name: str, owner_id: int):
        try:
            async with self.get_session() as session:
                instance = Business(name=name, owner_id=owner_id)
                session.add(instance)
            return instance
        except IntegrityError as exc:
            raise BadRequest(f"IntegrityError: maybe there are no user with id: {owner_id}")

    async def get_business(self, business_id: int):
        async with self.get_session() as session:
            instance = await self._get_business(business_id, session)
        await self.cache_object(instance)
        return instance

    @staticmethod
    async def _get_business(business_id: int, session: AsyncSession):
        query = select(Business).where(Business.id == business_id)
        res = await session.execute(query)
        return res.scalars().first()


business_service = BusinessService(async_session_factory)
