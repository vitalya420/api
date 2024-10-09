from typing import Optional

from app.db import async_session_factory
from app.models import User
from app.repositories.user import UserRepository
from .base import BaseService


class UserService(BaseService):
    __repository_class__ = UserRepository

    async def create(
        self,
        phone: str,
        *,
        password: Optional[str] = None,
        business_name: Optional[str] = None,
        is_admin: Optional[bool] = False,
    ) -> User:
        async with self.get_repo() as user_repo:
            new_user = await user_repo.create_user(
                phone, password, business_name, is_admin
            )
        return new_user

    async def get_or_create(self, phone: str):
        async with self.get_repo() as user_repo:
            if existing_user := await user_repo.get_user(phone=phone):
                return existing_user
            await user_repo.create_user(phone=phone)
            return await user_repo.get_user(phone=phone)

    async def get_user(
        self,
        pk: Optional[int] = None,
        phone: Optional[str] = None,
        use_cache: bool = True,
    ):
        async with self.get_repo() as user_repo:
            if use_cache:
                return await self.with_cache(
                    User, pk or phone, user_repo.get_user, pk=pk, phone=phone
                )
            return await user_repo.get_user(pk=pk, phone=phone)


user_service = UserService(async_session_factory)
