from typing import Optional

from app.db import async_session_factory
from app.models import User
from app.repositories.user import UserRepository
from app.base import BaseService


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
        """
        Create a new user with the specified phone number and optional details.

        This method creates a new User instance with the provided phone number,
        and optionally sets a password, business name, and admin status.

        Args:
            phone (str): The phone number of the user, formatted in international format (e.g., +1234567890).
            password (Optional[str]): The password for the user account, if applicable.
            business_name (Optional[str]): The name of the business associated with the user, if applicable.
            is_admin (Optional[bool]): A flag indicating whether the user should have admin privileges. Defaults to False.

        Returns:
            User: The newly created User instance.
        """
        async with self.get_repo() as user_repo:
            new_user = await user_repo.create_user(
                phone, password, business_name, is_admin
            )
        return new_user

    async def get_or_create(self, phone: str):
        """
        Retrieve an existing user or create a new one if it does not exist.

        This method checks if a user with the specified phone number already exists.
        If the user exists, it returns the existing user; otherwise, it creates a new user.

        Args:
            phone (str): The phone number of the user, formatted in international format (e.g., +1234567890).

        Returns:
            User: The existing or newly created User instance.
        """
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
        """
        Retrieve a user by primary key or phone number.

        This method queries the repository for a User instance that matches the provided
        primary key or phone number. It can optionally use caching for improved performance.

        Args:
            pk (Optional[int]): The primary key of the user to retrieve.
            phone (Optional[str]): The phone number of the user to retrieve, formatted in international format (e.g., +1234567890).
            use_cache (bool, optional): Whether to use the cache for retrieval. Defaults to True.

        Returns:
            Union[User, None]: The User instance if found, or None if not found.
        """
        async with self.get_repo() as user_repo:
            if use_cache:
                return await self.with_cache(
                    User, pk or phone, user_repo.get_user, pk=pk, phone=phone
                )
            return await user_repo.get_user(pk=pk, phone=phone)

    async def set_user_password(self, phone: str, password: str):
        """
        Set or update the password for a user identified by their phone number.

        This method updates the password for the user associated with the specified phone number.

        Args:
            phone (str): The phone number of the user whose password is to be set, formatted in international format (e.g., +1234567890).
            password (str): The new password for the user account.

        Returns:
            None: This method does not return a value.
        """
        async with self.get_repo() as user_repo:
            await user_repo.set_user_password(phone, password)


user_service = UserService(async_session_factory)
