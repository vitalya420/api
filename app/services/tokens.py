from datetime import datetime
from typing import Union, Literal

from sanic import Request, NotFound, Unauthorized
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.db import async_session_factory
from app.models import User, RefreshToken, AccessToken
from .base import BaseService


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
            return ("access", jti), ("refresh", refresh_jti)

    async def get_token_by_jti(self, type_: Union[str, Literal["access", "refresh"]],
                               jti: str):
        cls_ = AccessToken if type_ == "access" else RefreshToken
        query = select(cls_).where(and_(eq(cls_.jti, jti), eq(cls_.revoked, False)))
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def refresh(self, payload: dict[str, Union[str, int, bool]]):
        need_to_delete_from_cache = []
        async with self.get_session() as session:
            refresh = await self._get_token(payload['user_id'], payload['business'], payload['jti'], session, "refresh")
            if not refresh or not refresh.is_alive():
                raise Unauthorized("This refresh token is revoked or expired")

            await self._revoke_token_unsafe("refresh", refresh.jti, session)
            need_to_delete_from_cache.append(("refresh", refresh.jti))

            access = await self._get_access_token_by_refresh_jti(payload['jti'], session)
            print('access', access)
            if access.is_alive():
                await self._revoke_token_unsafe("access", access.jti, session)
                need_to_delete_from_cache.append(("access", access.jti))
        new_tokens = await self.issue_token_pair(payload['user_id'], payload['business'])
        return need_to_delete_from_cache, new_tokens

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

    async def _get_token(self, user_id: int, business: str, jti: str,
                         session: AsyncSession,
                         type_: Union[
                             str, Literal["access", "refresh"]] = "access") -> AccessToken | RefreshToken | None:
        cls_ = AccessToken if type_ == 'access' else RefreshToken
        query = select(cls_).where(and_(
            cls_.jti == jti,
            cls_.user_id == user_id,
            cls_.business == business,
            cls_.revoked == False,
        ))
        result = await session.execute(query)
        return result.scalars().first()

    async def _revoke_token_unsafe(self, type_: Union[str, Literal["access", "refresh"]], jti: str,
                                   session: AsyncSession):
        cls_ = AccessToken if type_ == "access" else RefreshToken
        query = update(cls_).where(cls_.jti == jti).values(revoked=True)  # noqa
        result = await session.execute(query)

    async def _get_access_token_by_refresh_jti(self, refresh_jti: str, session: AsyncSession):
        query = select(AccessToken).where(eq(AccessToken.refresh_token_jti, refresh_jti))
        result = await session.execute(query)
        return result.scalars().first()


tokens_service = TokenService(async_session_factory)
