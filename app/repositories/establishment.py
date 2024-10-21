from typing import Optional, Union, Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.base import BaseRepository
from app.models import Establishment, Address, Business, EstablishmentWorkSchedule


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

    async def get_establishment(self, est_id: int) -> Union[Establishment, None]:
        query = (
            select(Establishment)
            .where(Establishment.id == est_id)
            .options(
                joinedload(Establishment.address),
                joinedload(Establishment.business),
                joinedload(Establishment.work_schedule).options(
                    joinedload(EstablishmentWorkSchedule.monday_schedule),
                    joinedload(EstablishmentWorkSchedule.tuesday_schedule),
                    joinedload(EstablishmentWorkSchedule.wednesday_schedule),
                    joinedload(EstablishmentWorkSchedule.thursday_schedule),
                    joinedload(EstablishmentWorkSchedule.friday_schedule),
                    joinedload(EstablishmentWorkSchedule.saturday_schedule),
                    joinedload(EstablishmentWorkSchedule.sunday_schedule),
                ),
            )
        )
        res = await self.session.execute(query)
        return res.scalars().first()

    async def get_business_establishments(
        self, business_code: str
    ) -> Sequence[Establishment]:
        query = (
            select(Establishment)
            .where(Establishment.business_code == business_code)
            .options(
                joinedload(Establishment.address),
                joinedload(Establishment.business),
                joinedload(Establishment.work_schedule).options(
                    joinedload(EstablishmentWorkSchedule.monday_schedule),
                    joinedload(EstablishmentWorkSchedule.tuesday_schedule),
                    joinedload(EstablishmentWorkSchedule.wednesday_schedule),
                    joinedload(EstablishmentWorkSchedule.thursday_schedule),
                    joinedload(EstablishmentWorkSchedule.friday_schedule),
                    joinedload(EstablishmentWorkSchedule.saturday_schedule),
                    joinedload(EstablishmentWorkSchedule.sunday_schedule),
                ),
            )
        )
        res = await self.session.execute(query)
        return res.scalars().all()

    async def update_establishment_image(self, user_id: int, est_id: int, image: str):
        query = (
            select(Establishment)
            .join(Establishment.business)
            .filter(Establishment.id == est_id, Business.owner_id == user_id)
            .options(joinedload(Establishment.business))
        )
        res = await self.session.execute(query)
        establishment = res.scalars().first()
        if establishment:
            establishment.image = image
        await self.session.flush()
