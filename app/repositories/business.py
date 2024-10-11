from typing import Union

from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.operators import eq

from app.base import BaseRepository
from app.models import User, Business, BusinessClient
from app.utils import force_id


class BusinessRepository(BaseRepository):
    """
    Repository class for managing business-related database operations.

    This class provides methods to create and retrieve business entities from the database.
    It extends the BaseRepository to leverage common database functionalities.
    """

    async def create_business(self, name: str, user: Union[User, int]) -> Business:
        """
        Create a new business entity.

        This method initializes a new Business instance with the provided name and associates
        it with the specified user. The user can be provided as a User object or as an integer
        representing the user ID.

        Args:
            name (str): The name of the business to be created.
            user (Union[User, int]): The user associated with the business, either as a User
                object or as an integer representing the user ID.

        Returns:
            Business: The newly created Business instance.

        Example:
            repository = BusinessRepository(session)
            new_business = await repository.create_business("My Business", user_id)
        """

        business = Business(name=name, owner_id=force_id(user))
        self.session.add(business)
        return business

    async def get_business(self, code: str) -> Union[Business, None]:
        """
        Retrieve a business entity by its unique code.

        This method queries the database for a Business instance that matches the provided
        unique code. If found, it returns the Business instance; otherwise, it returns None.

        Args:
            code (str): The unique code of the business to retrieve.

        Returns:
            Union[Business, None]: The Business instance if found, or None if not found.

        Example:
            repository = BusinessRepository(session)
            business = await repository.get_business("BUSINESS_CODE")
        """
        query = (
            select(Business)
            .where(Business.code == code)
            .options(joinedload(Business.owner))
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def get_client(
        self, business_code: str, user_id: int
    ) -> Union[BusinessClient, None]:
        """
        Retrieve a BusinessClient instance by business code and user ID.

        This method queries the database for a BusinessClient instance that matches the
        provided business code and user ID. If found, it returns the BusinessClient instance;
        otherwise, it returns None.

        Args:
            business_code (str): The unique code of the business associated with the client.
            user_id (int): The unique identifier of the user.

        Returns:
            Union[BusinessClient, None]: The BusinessClient instance if found, or None if not found.

        Example:
            client = await repository.get_client("BUSINESS_CODE", 123)
        """
        query = (
            select(BusinessClient)
            .where(
                and_(
                    eq(BusinessClient.business_code, business_code),
                    eq(BusinessClient.user_id, user_id),
                )
            )
            .options(
                joinedload(BusinessClient.business),
                joinedload(BusinessClient.user),
            )
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def add_client(self, business_code: str, user_id: int) -> BusinessClient:
        """
        Add a new BusinessClient instance to the database.

        This method creates a new BusinessClient instance with the provided business code
        and user ID, and adds it to the session. The instance is flushed to the database
        to ensure it is saved.

        Args:
            business_code (str): The unique code of the business associated with the client.
            user_id (int): The unique identifier of the user.

        Returns:
            BusinessClient: The newly created BusinessClient instance.

        Example:
            new_client = await repository.add_client("BUSINESS_CODE", 123)
        """
        instance = BusinessClient(
            user_id=user_id, business_code=business_code, first_name=f"User {user_id}"
        )
        self.session.add(instance)
        await self.session.flush()
        return instance
