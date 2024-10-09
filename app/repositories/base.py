from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def flush(self, objects=None):
        await self.session.flush(objects)
