from typing import Union

from sqlalchemy import select

from .base import BaseRepository
from app.models import User, Business
from app.utils import force_id


class BusinessRepository(BaseRepository):
    async def create_business(self, name: str, user: Union[User, int]) -> Business:
        business = Business(name=name, owner_id=force_id(user))
        self.session.add(business)
        return business

    async def get_business(self, code: str) -> Union[Business, None]:
        query = select(Business).where(Business.code == code)
        res = await self.session.execute(query)
        return res.scalars().first()
