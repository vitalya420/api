import asyncio
import time
from pprint import pprint

from app.base import BaseService
from app.redis import connect
from app.enums import Realm
from app.routes.mobile.v1 import business
from app.schemas import BusinessResponse
from app.services import user_service, tokens_service, business_service


async def create_business(name: str, owner_id: int):
    pass


async def create_business_user(phone: str, name: str):
    pass


async def main():
    redis_ = await connect()
    BaseService.set_redis(redis_)

    # await business_service.create_business("Naggers Shop",
    #                                        (await user_service.get_user(phone="+380956409567")).id)

    await business_service.create_establishment(
        "JAJLAVWWCMVCMTMH", address="america", long=13.13, lat=44.44
    ),
    user = await user_service.get_user(phone="+380956409567", use_cache=False)
    pprint(BusinessResponse.model_validate(user.business).model_dump())


if __name__ == "__main__":
    asyncio.run(main())
