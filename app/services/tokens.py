from datetime import datetime
from typing import Union, Literal

from sanic import Request, NotFound
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session_factory
from app.models import User, RefreshToken, AccessToken
from .base import BaseService
from ..utils.tokens import remove_token_from_cache


class TokenService(BaseService):
    async def issue_token_pair(self, user_or_id: Union[User, int], business):
        user_id = user_or_id if isinstance(user_or_id, int) else user_or_id.id
        async with self.session_factory() as session:
            access, refresh = await self._create_tokens_using_context(user_id, business, session)
        return access, refresh

    async def revoke_token(self, user_or_id: Union[User, int], business, jti: str):
        user_id = user_or_id if isinstance(user_or_id, int) else user_or_id.id
        now = datetime.utcnow()

        async with self.get_session() as session:
            access_token = await self._get_token(user_id, business, jti, session)

            if not access_token:
                raise NotFound

            refresh_jti = access_token.refresh_token_jti
            await self._revoke_token_unsafe("access", jti, session)
            await self._revoke_token_unsafe("refresh", refresh_jti, session)

    async def get_user_tokens(self, user_or_id: Union[User, int], business: str):
        user_id = user_or_id if isinstance(user_or_id, int) else user_or_id.id
        now = datetime.utcnow()  # noqa

        query = select(AccessToken).where(
            and_(
                AccessToken.user_id == user_id,
                AccessToken.business == business,
                AccessToken.revoked == False,
                AccessToken.expires_at >= now
            )
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

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

    async def _get_token(self, user_id: int, business: str, jti: str, session: AsyncSession) -> AccessToken | None:
        query = select(AccessToken).where(and_(
            AccessToken.jti == jti,
            AccessToken.user_id == user_id,
            AccessToken.business == business,
            AccessToken.revoked == False,
        ))
        result = await session.execute(query)
        return result.scalars().first()

    async def _revoke_token_unsafe(self, type_: Union[str, Literal["access", "refresh"]], jti: str,
                                   session: AsyncSession):
        cls_ = AccessToken if type_ == "access" else RefreshToken
        query = update(cls_).where(cls_.jti == jti).values(revoked=True) # noqa
        result = await session.execute(query)
        if result.rowcount:
            await remove_token_from_cache(jti, type_, self.cls_context['redis'])


tokens_service = TokenService(async_session_factory)
