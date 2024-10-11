from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import User
from app.base import BaseRepository
from app.exceptions import UserExists, YouAreRetardedError, UserDoesNotExist
from app.repositories.business import BusinessRepository


class UserRepository(BaseRepository):
    """
    Repository for managing user accounts in the database.

    This class provides methods to create users, retrieve user information, and manage user passwords.
    It interacts with the database using SQLAlchemy ORM.
    """

    async def create_user(
        self,
        phone: str,
        password: Optional[str] = None,
        business_name: Optional[str] = None,
        is_admin: Optional[bool] = False,
    ) -> User:
        """
        Creates a new user with the specified phone number and optional attributes.

        Args:
            phone (str): The phone number of the user to be created.
            password (Optional[str]): The password for the user (required for business users).
            business_name (Optional[str]): The name of the business associated with the user (required for business users).
            is_admin (Optional[bool]): Indicates if the user is an admin (default is False).

        Returns:
            User: The newly created user.

        Raises:
            UserExists: If a user with the specified phone number already exists.
            YouAreRetardedError: Something unexpected happened because of you.
        """
        existing_user = await self.get_user(phone=phone)
        if existing_user:
            raise UserExists(f"User with phone {phone} already exists.")

        new_user = User(phone=phone, is_admin=is_admin)
        self.session.add(new_user)
        await self.session.flush()

        if (is_business_user := not not password) and not business_name:
            raise YouAreRetardedError(
                "Business users have password but you did not provided business name to create"
            )

        if is_business_user:
            new_user.set_password(password)
            await self.session.flush()
            await BusinessRepository(self.session).create_business(
                business_name, new_user
            )
        return new_user

    async def get_user(
        self, *, pk: Optional[int] = None, phone: [str] = None
    ) -> Union[User, None]:
        """
        Retrieves a user by primary key (pk) or phone number.

        Args:
            pk (Optional[int]): The primary key of the user to retrieve.
            phone (Optional[str]): The phone number of the user to retrieve.

        Returns:
            Union[User, None]: The retrieved user, or None if not found.

        Raises:
            ValueError: If neither pk nor phone is provided, or if both are provided.
        """
        if (not pk and not phone) or (pk and phone):
            raise ValueError("Either pk or phone is required")
        where_clause = None
        if pk:
            where_clause = User.id == pk
        elif phone:
            where_clause = User.phone == phone
        query = select(User).where(where_clause).options(joinedload(User.businesses))
        res = await self.session.execute(query)
        return res.scalars().first()

    async def set_user_password(self, phone: str, password: str):
        """
        Sets a new password for an existing user identified by their phone number.

        Args:
            phone (str): The phone number of the user whose password is to be set.
            password (str): The new password for the user.

        Raises:
            UserDoesNotExist: If no user with the specified phone number exists.
        """
        user = await self.get_user(phone=phone)
        if not user:
            raise UserDoesNotExist("User with phone does not exist.")
        user.set_password(password)
