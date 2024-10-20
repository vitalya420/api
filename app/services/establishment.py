from app.base import BaseService
from app.repositories.establishment import EstablishmentRepository


class EstablishmentService(BaseService):
    __repository_class__ = EstablishmentRepository

    async def get_establishment(self, pk: int):
        pass

    async def create_establishment(self):
        pass

    async def update_establishment(self, pk: int, **data):
        pass

    async def set_work_schedule(self, pk: int):
        pass
