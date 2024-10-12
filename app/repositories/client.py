from typing import Union, Sequence

from sqlalchemy import select

from app.base import BaseRepository
from app.models import Client, Coupon


class ClientRepository(BaseRepository):
    async def get_client(self, pk: int) -> Union[Client, None]:
        query = select(Client).where(Client.id == pk)
        res = await self.session.execute(query)
        return res.scalars().first()

    async def create_client(self, user_id: int, business_code: str) -> Client:
        client = Client(
            user_id=user_id, business_code=business_code, first_name=f"User {user_id}"
        )
        self.session.add(client)
        return client

    async def get_client_coupons(self, pk: int) -> Sequence[Coupon]:
        query = select(Coupon).where(Coupon.client_id == pk)
        res = await self.session.execute(query)
        return res.scalars().all()
