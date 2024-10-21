from typing import Union, Optional

from app.base import BaseService
from app.db import async_session_factory
from app.enums import DayOfWeek
from app.models import User, Business
from app.repositories.establishment import EstablishmentRepository
from app.utils import force_id


class EstablishmentService(BaseService):
    __repository_class__ = EstablishmentRepository

    async def get_establishment(self, pk: int):
        pass

    async def create_establishment(
        self,
        business: Union[Business, str],
        address: Optional[str] = None,
        long: Optional[float] = None,
        lat: Optional[float] = None,
        image: Optional[str] = None,
    ):
        _isolated_service = self.isolate()
        async with _isolated_service.get_repo() as est_repo:
            business = (
                await _isolated_service.get_business(business)
                if isinstance(business, str)
                else business
            )
            await self.cache_delete_object(business)
            await self.cache_delete_object(business.owner)  # noqa
            created = await est_repo.create(
                business.code, business.name, address, long, lat, image  # noqa
            )
        return created

    async def update_establishment(self, pk: int, **new_data):
        async with self.get_repo() as repo:
            repo: EstablishmentRepository = repo
            est = await repo.get_establishment(pk)
            for key, value in new_data.items():
                setattr(est.address, key, value)
        return est

    async def set_establishment_image(
        self, est_id: int, owner: Union[User, int], image_url: str
    ):
        async with self.get_repo() as est_repo:
            await est_repo.update_establishment_image(
                force_id(owner), est_id, image_url
            )
            if isinstance(owner, User):
                await self.cache_delete_object(owner)
            elif isinstance(owner, int):
                await self.cache_delete(User.lookup_key(owner))

            return await est_repo.get_establishment(est_id)

    async def delete_establishment(self, owner: Union[User, int], est_id: int):
        isolated = self.isolate()
        async with isolated.get_repo() as est_repo:
            est = await est_repo.get_establishment(est_id)
            if est and est.business.owner_id == force_id(owner):
                await self.cache_delete_object(est.business)
                await isolated.get_running_session().delete(est)
            if isinstance(owner, User):
                await self.cache_delete_object(owner)
            elif isinstance(owner, int):
                await self.cache_delete(User.lookup_key(owner))

        return est

    async def set_work_schedule(self, pk: int, **schedule):
        for day, day_schedule in schedule.items():
            day = DayOfWeek(day)
            print(day, day_schedule)


establishment_service = EstablishmentService(
    async_session_factory, context={"_is_default": True}
)
