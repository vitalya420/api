from typing import Optional

from app.base import BaseRepository
from app.models import Establishment, Address


class EstablishmentRepository(BaseRepository):

    async def create(
        self,
        business_code: str,
        name: str,
        address: Optional[str] = None,
        long: Optional[float] = None,
        lat: Optional[float] = None,
        image: Optional[str] = None,
    ):
        addr: Optional[Address] = None
        if address or (long is not None and lat is not None):
            addr = Address(address=address, longitude=long, latitude=lat)
            self.session.add(addr)

        instance = Establishment(
            business_code=business_code, image=image, name=name, address=addr
        )
        self.session.add(instance)

        await self.session.flush()
        return instance
