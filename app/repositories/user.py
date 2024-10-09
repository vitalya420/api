from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import User
from .base import BaseRepository
from app.exceptions import UserExists, YouAreRetardedError
from .business import BusinessRepository


class UserRepository(BaseRepository):
    async def create_user(
        self,
        phone: str,
        password: Optional[str] = None,
        business_name: Optional[str] = None,
        is_admin: Optional[bool] = False,
    ) -> User:
        existing_user = await self.get_user(phone=phone)
        if existing_user:
            raise UserExists(f"User with phone {phone} already exists.")

        new_user = User(phone=phone, is_admin=is_admin)
        self.session.add(new_user)
        await self.session.flush()

        if (is_business_user := not not password) and not business_name:
            raise YouAreRetardedError(
                "Business users have passwords but you did not provided business name to create"
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
        if (not pk and not phone) or (pk and phone):
            raise ValueError("Either pk or phone is required")
        where_clause = None
        if pk:
            where_clause = User.id == pk
        if phone:
            where_clause = User.phone == phone
        query = select(User).where(where_clause).options(joinedload(User.businesses))
        res = await self.session.execute(query)
        return res.scalars().first()
