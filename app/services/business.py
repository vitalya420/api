import asyncio
from typing import Union

from sqlalchemy.exc import IntegrityError

from app.base import BaseService
from app.db import async_session_factory
from app.exceptions import UnableToCreateBusiness
from app.models import Business, User, Client
from app.repositories import BusinessRepository
from app.services import user_service
from app.utils import force_id, force_code


class BusinessService(BaseService):
    __repository_class__ = BusinessRepository

    async def create_business(self, name: str, owner: Union[User, int]):
        """
        Create a new business and associate it with the specified owner.

        This method attempts to create a new Business instance with the provided name
        and owner. If successful, it updates the cache for the owner to reflect the
        new business association.

        Args:
            name (str): The name of the business to be created.
            owner (Union[User, int]): The owner of the business, which can be a User
                                       instance or the user's ID.

        Returns:
            Business: The newly created Business instance.

        Raises:
            UnableToCreateBusiness: If there is an integrity error during the creation
                                    of the business, such as the owner not existing.
        """
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
        """
        Retrieve a business entity by its unique business code.

        This method queries the repository for a Business instance that matches the
        provided business code. It can optionally use a cache to improve performance.

        Args:
            business_code (str): The unique code of the business to retrieve.
            use_cache (bool, optional): Whether to use the cache for retrieval. Defaults to True.

        Returns:
            Union[Business, None]: The Business instance if found, or None if not found.
        """
        async with self.get_repo() as business_repo:
            if use_cache:
                return await self.with_cache(
                    Business, business_code, business_repo.get_business, business_code
                )
            return await business_repo.get_business(business_code)

    async def get_clients(
        self,
        business: Union[Business, str],
        staff_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ):
        """
        Retrieve a list of clients associated with a specific business.

        This method queries the repository for clients linked to the specified business,
        applying pagination through limit and offset parameters.

        Args:
            business (Union[Business, str]): The business instance or its unique code.
            limit (int, optional): The maximum number of clients to retrieve. Defaults to 20.
            offset (int, optional): The number of clients to skip before starting to collect the result set. Defaults to 0.

        Returns:
            List[BusinessClient]: A list of BusinessClient instances associated with the business.
        """
        async with self.get_repo() as business_repo:
            result = await business_repo.get_clients(
                force_code(business), staff_only, limit, offset
            )
        return result

    async def get_or_create_client(
        self, business: Union[Business, str], user: Union[User, int]
    ) -> Union[Client, None]:
        """
        Retrieve an existing client or create a new one if it does not exist.

        This method checks if a BusinessClient instance exists for the specified business
        and user. If it exists, it returns the client; otherwise, it creates a new client.

        Args:
           business (Union[Business, str]): The business instance or its unique code.
           user (Union[User, int]): The user instance or the user's ID.

        Returns:
           Union[Client, None]: The existing or newly created BusinessClient instance.
        """
        async with self.get_repo() as business_repo:
            if existing_client := await business_repo.get_client(
                force_code(business), force_id(user)
            ):
                await self.cache_object(existing_client)
                return existing_client

            await business_repo.add_client(force_code(business), force_id(user))
            # returned instance is not joined,
            # so let's get it joined and cache it!
        return await self.get_client(business, user)

    async def get_client(
        self,
        business: Union[Business, str],
        user: Union[User, int],
        use_cache: bool = True,
    ) -> Union[Client, None]:
        """
        Retrieve a specific client associated with a business.

        This method queries the repository for a BusinessClient instance that matches
        the specified business and user. It can optionally use a cache to improve performance.

        Args:
            business (Union[Business, str]): The business instance or its unique code.
            user (Union[User, int]): The user instance or the user's ID.
            use_cache (bool, optional): Whether to use the cache for retrieval. Defaults to True.

        Returns:
            Union[BusinessClient, None]: The BusinessClient instance if found, or None if not found.
        """
        async with self.get_repo() as business_repo:
            if use_cache:
                user_id, business_code = force_id(user), force_code(business)
                key = f"{user_id}:{business_code}"

                return await self.with_cache(
                    Client,
                    key,
                    business_repo.get_client,
                    business_code,
                    user_id,
                )
            return await business_repo.get_client(force_code(business), force_id(user))

    async def update_client(self, client: Client, **new_data):
        """
        Update the attributes of a BusinessClient instance with new data.

        This method merges the provided BusinessClient instance with the current session,
        deletes the cached version of the client, and updates its attributes based on the
        provided keyword arguments. Only attributes that exist on the BusinessClient instance
        and have non-None values will be updated.

        Args:
            client (BusinessClient): The BusinessClient instance to be updated.
            **new_data: Arbitrary keyword arguments representing the attributes to be updated
                         and their new values.

        Returns:
            BusinessClient: The updated BusinessClient instance after merging changes.

        Raises:
            Exception: If there is an error during the session merge or attribute setting.
        """
        async with self.get_session() as session:
            await self.cache_delete_object(client)
            merged = await session.merge(client)
            for key, value in new_data.items():
                if hasattr(merged, key) and value is not None:
                    setattr(merged, key, value)
        return merged

    async def count_clients(
        self, business: Union[Business, str], staff_only: bool = False
    ) -> int:
        async with self.get_repo() as repo:
            return await repo.count_clients(force_code(business), staff_only)


business_service = BusinessService(async_session_factory)
