from typing import Union

from sanic import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_factory
from app.models import User, RefreshToken, AccessToken
from .base import BaseService


class TokenService(BaseService):
    async def issue_token_pair(self, user_or_id: Union[User, int], business):
        user_id = user_or_id if isinstance(user_or_id, int) else user_or_id.id
        async with self.session_factory() as session:
            access, refresh = await self._create_tokens_using_context(user_id, business, session)
        return access, refresh

    async def _create_tokens_using_context(self, user_id: int, business: str, session: AsyncSession):
        request: Request | None = self.context.get('request', None)
        if request is None:
            raise RuntimeError("Need to provide request in context")
        ip_addr = request.headers.get('X-Real-IP', "<no ip>")
        user_agent = request.headers.get('User-Agent', "<no agent>")

        refresh = RefreshToken(user_id=user_id, business=business)
        session.add(refresh)
        await session.commit()

        access = AccessToken(user_id=user_id, business=business,
                             ip_addr=ip_addr, user_agent=user_agent,
                             refresh_token_jti=refresh.jti)
        session.add(access)
        await session.commit()

        await session.refresh(access)

        return access, refresh


tokens = TokenService(async_session_factory)
