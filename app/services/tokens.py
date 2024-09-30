from datetime import datetime
from typing import Union, Literal, Optional

from sanic import BadRequest
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from .base import BaseService
from app.models import AccessToken, RefreshToken
from app.security import decode_token
from ..db import async_session_factory


class TokenService(BaseService):
    async def issue_new_tokens(self, refresh_token: str):
        payload = decode_token(refresh_token)
        type_ = payload['type']
        if type_ != 'refresh':
            raise BadRequest

        async with self.session_factory() as session:
            async with session.begin():
                token = await self._get_token_by_jti(type_, payload['jti'], session)
                if not token:
                    raise BadRequest("Refresh token is invalid")

                await self._revoke_token("refresh", payload['jti'], session)

    async def get_all_users_tokens(self,
                                   type_: Union[str, Literal["access", "refresh"]] = "access",
                                   user_id: Optional[int] = None,
                                   limit: int = 10,
                                   offset: int = 0):
        if type_ not in ["access", "refresh"]:
            raise ValueError("Type must be either access or refresh")
        if not user_id and not self.context.get('user_id', None):
            raise RuntimeError("user_id should be provided via context or as argument")

        cls_ = AccessToken if type_ == "access" else RefreshToken

        now = datetime.utcnow()

        query = select(cls_).where(and_(
            eq(cls_.user_id, user_id or self.context['user_id']),
            eq(cls_.revoked, False),
            cls_.expires_at > now
        )).limit(limit).offset(offset)

        async with self.session_factory() as session:
            result = await session.execute(query)
            tokens = result.scalars().all()

        return tokens

    @staticmethod
    async def _get_token_by_jti(type_: Union[str, Literal["access", "refresh"]],
                                jti: str,
                                session: AsyncSession):
        now = datetime.utcnow()
        cls_ = AccessToken if type_ == "access" else RefreshToken
        query = select(cls_).where(
            and_(
                and_(
                    eq(cls_.jti, jti),
                    eq(cls_.revoked, False)
                )
            ),
            cls_.expires_at > now)  # noqa
        res = await session.execute(query)
        return res.scalars().first()

    @staticmethod
    async def _revoke_token(type_: Union[str, Literal["access", "refresh"]],
                            jti: str,
                            session: AsyncSession,
                            do_commit: bool = False):
        cls_ = AccessToken if type_ == "access" else RefreshToken
        query = update(cls_).where(eq(cls_.jti, jti)).values(revoked=True)
        result = await session.execute(query)
        if do_commit:
            await session.commit()
        return result


tokens = TokenService(async_session_factory)
