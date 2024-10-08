import asyncio

from app.services import user_service


async def create_business(name: str, owner_id: int):
    pass


async def create_business_user(phone: str, name: str):
    pass


async def main():
    # await user_service.create(
    #     "+380956409522",
    #     password="fuckyeah",
    #     business_name="Retards Corp.",
    #     is_admin=True,
    # )

    user = await user_service.get_user("+380956409522")
    print(user.businesses)


if __name__ == '__main__':
    asyncio.run(main())
