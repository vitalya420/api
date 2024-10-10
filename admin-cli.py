import asyncio
import time

from app.base import BaseService
from app.redis import connect
from app.schemas.enums import Realm
from app.services import user_service, tokens_service, business_service


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

    # await user_service.set_user_password("+380956409567", 'fuckyeah')
    # await business_service.create_business("Coffee Shop", (await user_service.get_user(phone="+380956409567")).id)

    start = time.time()
    for _ in range(5000):
        user = await user_service.get_user(phone="+380956409567", use_cache=True)
    end = time.time()
    print(f"Time elapsed using reference {end - start:02f} seconds")

    start = time.time()
    for _ in range(5000):
        user = await user_service.get_user(pk=1, use_cache=True)
    end = time.time()
    print(f"Time elapsed using main key {end - start:02f} seconds")

    start = time.time()
    for _ in range(5000):
        user = await user_service.get_user(pk=1, use_cache=False)
    end = time.time()
    print(f"Time elapsed with no caching {end - start:02f} seconds")

if __name__ == '__main__':
    asyncio.run(main())
