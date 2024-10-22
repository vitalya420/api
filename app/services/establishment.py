from typing import Union, Optional, Sequence

from sanic import NotFound

from app.base import BaseService
from app.db import async_session_factory
from app.models import User, Business, Address, Establishment, EstablishmentWorkSchedule
from app.models.work_schedule import DayScheduleInfo
from app.repositories.establishment import EstablishmentRepository
from app.utils import force_id, force_code


class EstablishmentService(BaseService):
    __repository_class__ = EstablishmentRepository

    async def get_establishment(self, pk: int) -> Union[Establishment, None]:
        async with self.get_repo() as repo:
            instance = await repo.get_establishment(pk)
        return instance

    async def get_business_establishments(
        self, business: Union[Business, str]
    ) -> Sequence[Establishment]:
        async with self.get_repo() as repo:
            instances = await repo.get_business_establishments(force_code(business))
        return instances

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
            if est.address is None:
                address = Address(**new_data)
                repo.session.add(address)
                await repo.session.flush()
            else:
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
        async with self.get_session() as session:
            contexted = self.with_context({"session": session})
            establishment = await contexted.get_establishment(pk)
            if establishment is None:
                return

            if establishment.work_schedule is None:
                day_schedules = {}
                for day, day_schedule in schedule.items():
                    instance = DayScheduleInfo(**day_schedule)
                    day_schedules[f"{day}_schedule"] = instance
                schedule = EstablishmentWorkSchedule(
                    establishment_id=pk, **day_schedules
                )
                session.add_all([schedule, *day_schedules.values()])
            else:
                for day, day_schedule in schedule.items():
                    existed_instance = getattr(
                        establishment.work_schedule, f"{day}_schedule"
                    )
                    for k, v in day_schedule.items():
                        setattr(existed_instance, k, v)
                    session.add(existed_instance)
            est = await contexted.get_establishment(pk)
        return est

    async def user_deletes_schedule(self, user: Union[User, int], est_id: int):
        async with self.get_session() as session:
            contexted = self.with_context({"session": session})
            establishment = await contexted.get_establishment(est_id)
            if (
                establishment
                and establishment.business.owner_id == force_id(user)  # noqa
                and establishment.work_schedule
            ):
                await session.delete(establishment.work_schedule)
            else:
                raise NotFound("No estimated with associated logged in user")


establishment_service = EstablishmentService(
    async_session_factory, context={"_is_default": True}
)
