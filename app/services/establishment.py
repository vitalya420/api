from app.base import BaseService
from app.enums import DayOfWeek
from app.repositories.establishment import EstablishmentRepository


class EstablishmentService(BaseService):
    __repository_class__ = EstablishmentRepository

    async def get_establishment(self, pk: int):
        pass

    async def create_establishment(self):
        pass

    async def update_establishment(self, pk: int, **data):
        pass

    async def set_establishment_image(self, pk, owner, image_url):
        pass

    async def set_work_schedule(self, pk: int, **schedule):
        for day, day_schedule in schedule.items():
            day = DayOfWeek(day)
            print(day, day_schedule)

