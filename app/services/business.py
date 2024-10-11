import asyncio
from typing import Union

from sqlalchemy.exc import IntegrityError

from app.base import BaseService
from app.db import async_session_factory
from app.exceptions import UnableToCreateBusiness
from app.models import Business, User
from app.repositories import BusinessRepository
from app.services import user_service
from app.utils import force_id


class BusinessService(BaseService):
    __repository_class__ = BusinessRepository

    async def create_business(self, name: str, owner: Union[User, int]):
        try:
            async with self.get_repo() as business_repo:
                instance = await business_repo.create_business(name, owner)

                # User just got updated, he has a new business now,
                # So we need to update in cache
                # Let's just delete him from cache, and updated user
                # will be cached again on his next request
                coro = self.cache_delete_object(
                    await user_service.get_user(force_id(owner), use_cache=False)
                )
                asyncio.create_task(coro)

            return instance
        except IntegrityError:
            raise UnableToCreateBusiness(
                f"IntegrityError: maybe there are no user with id: {force_id(owner)}"
            )

    async def get_business(
        self, business_code: str, use_cache: bool = True
    ) -> Union[Business, None]:
        async with self.get_repo() as business_repo:
            if use_cache:
                return await self.with_cache(
                    Business, business_code, business_repo.get_business, business_code
                )
            return await business_repo.get_business(business_code)


business_service = BusinessService(async_session_factory)
