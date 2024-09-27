from typing import Optional

from app.schemas import UserCreate
from app.services import services
from app.services.base import BaseService
from app.models import User as UserModel


@services("user")
class UserService(BaseService):

    def create_from_schema(self, user: UserCreate) -> None:
        print("Creating user from schema", user)

    async def create(self, first_name: str, phone: str, last_name: Optional[str] = None) -> UserModel:
        async with self.session_factory() as session:
            async with session.begin():
                instance = UserModel(first_name=first_name, last_name=last_name, phone=phone)
                session.add(instance)
            await session.refresh(instance)
            return instance
