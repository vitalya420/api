import asyncio
import time

from app import BaseService
from app.redis import connect
from app.schemas.enums import Realm
from app.services import user_service, tokens_service


async def create_business(name: str, owner_id: int):
    pass


async def create_business_user(phone: str, name: str):
    pass


async def main():
    redis_ = await connect()
    BaseService.set_redis(redis_)
    # await user_service.create(
    #     "+38095111113",
    #     password="fuckyeah",
    #     business_name="My Coffee Shop Corp.",
    #     is_admin=True,
    # )

    start = time.time()
    issued = await tokens_service.create_tokens(
        1, Realm.web
    )
    print(issued)


if __name__ == '__main__':
    asyncio.run(main())
