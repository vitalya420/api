import asyncio
import pickle
from datetime import datetime
from itertools import count
from typing import Union, Optional, List

from sanic import Request, BadRequest
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq
from typing_extensions import Sequence

from app.db import async_session_factory
from app.models import RefreshToken, AccessToken
from app.types import TokenType, UserType, BusinessType, get_token_class
from app.utils import force_id, force_business_code
from .base import BaseService


class TokenService(BaseService):
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

    async def user_revokes_access_token_by_jti(self, user: UserType, jti: str):
        query = select(AccessToken).where(
            and_(
                eq(AccessToken.jti, jti),
                eq(AccessToken.user_id, force_id(user)),
            ),
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            access_token = result.scalars().first()
            if access_token is None:
                return
            refresh_jti = access_token.refresh_token_jti

            await self._revoke_token_by_jti("access", access_token.jti, session)
            await self._revoke_token_by_jti("refresh", refresh_jti, session)

        await asyncio.gather(
            self.remove_cache(f'token:access:{access_token.jti}'),
            self.remove_cache(f'token:refresh:{access_token.refresh_token_jti}'),
        )

    async def refresh_tokens(self, refresh_jti: str):
        keys_to_remove_from_cache = []
        async with self.get_session() as session:
            refresh = await self._get_token("refresh", refresh_jti, session)
            if not refresh:
                raise BadRequest("This refresh token is not valid")
            await self._revoke_token_by_jti("refresh", refresh_jti, session)
            keys_to_remove_from_cache.append(f"token:refresh:{refresh.jti}")

            access = await self._get_access_token_by_refresh_jti(refresh_jti, session)
            if access.is_alive():
                await self._revoke_token_by_jti("access", access.jti, session)
            keys_to_remove_from_cache.append(f"token:access:{access.jti}")

            new_tokens = await (self.
                                with_context({'session': session}).
                                create_token_for_user(access.user_id, access.business))
        await asyncio.gather(*[self.remove_cache(key) for key in keys_to_remove_from_cache])
        return new_tokens

    async def revoke_access_token(self, access_token: AccessToken):
        async with self.get_session() as session:
            await self._revoke_token_by_jti("access", access_token.jti, session)
            await self._revoke_token_by_jti("refresh", access_token.refresh_token_jti, session)
        await asyncio.gather(
            self.remove_cache(f'token:access:{access_token.jti}'),
            self.remove_cache(f'token:refresh:{access_token.refresh_token_jti}'),
        )

    async def get_access_token_by_jti(self, jti: str):
        async with self.get_session() as session:
            return await self._get_token("access", jti, session)

    async def get_refresh_token_by_jti(self, jti: str):
        async with self.get_session() as session:
            return await self._get_token("refresh", jti, session)

    async def revoke_all(self, user: UserType, business: BusinessType, exclude: Optional[Sequence[str]] = None):
        exclude = exclude or []
        keys_to_remove_from_cache = []

        query = select(AccessToken).where(
            and_(
                eq(AccessToken.user_id, force_id(user)),
                eq(AccessToken.business, force_business_code(business)),
                eq(AccessToken.revoked, False),
                AccessToken.expires_at >= datetime.now() # noqa
            ),
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            tokens = result.scalars().all()

            counter = 0
            for token in tokens:
                access_jti = token.jti
                if access_jti in exclude:
                    continue

                refresh_jti = token.refresh_token_jti

                await self._revoke_token_by_jti("access", access_jti, session)
                await self._revoke_token_by_jti("refresh", refresh_jti, session)

                keys_to_remove_from_cache.extend([
                    f"token:access:{access_jti}",
                    f"token:refresh:{refresh_jti}"
                ])
                counter += 1
        await asyncio.gather(*[self.remove_cache(key) for key in keys_to_remove_from_cache])
        return counter

    async def create_token_for_user(self, user: UserType, business: BusinessType):
        async with self.get_session() as session:
            access, refresh = await self._create_tokens_using_context(
                force_id(user), force_business_code(business), session
            )
        await self.save_tokens_in_cache(access, refresh)
        return access, refresh

    async def list_user_issued_tokens_tokens(self, user: UserType, business: BusinessType, limit: int = 0,
                                             offset: int = 0):
        # TODO: Pagination
        query = select(AccessToken).where(
            and_(
                eq(AccessToken.user_id, force_id(user)),
                eq(AccessToken.business, force_business_code(business)),
                eq(AccessToken.revoked, False),
                AccessToken.expires_at >= datetime.utcnow()
            )
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def save_tokens_in_cache(self, *tokens: Union[AccessToken, RefreshToken]):
        await asyncio.gather(*[self.save_token_in_cache(token) for token in tokens])

    async def remove_tokens_from_cache(self, *tokens: Union[AccessToken, RefreshToken]):
        await asyncio.gather(*[self.remove_token_from_cache(token) for token in tokens])

    async def save_token_in_cache(self, token: Union[AccessToken, RefreshToken]):
        type_ = "access" if isinstance(token, AccessToken) else "refresh"
        await self.set_cache(f"token:{type_}:{token.jti}", pickle.dumps(token))

    async def remove_token_from_cache(self, token: Union[AccessToken, RefreshToken]):
        type_ = "access" if isinstance(token, AccessToken) else "refresh"
        await self.remove_cache(f"token:{type_}:{token.jti}")

    @staticmethod
    async def _get_access_token_by_refresh_jti(refresh_jti: str, session: AsyncSession):
        query = select(AccessToken).where(eq(AccessToken.refresh_token_jti, refresh_jti))
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def _revoke_token_by_jti(type_: TokenType, jti: str, session: AsyncSession):
        class_ = get_token_class(type_)
        query = update(class_).where(
            and_(
                eq(class_.jti, jti),
                eq(class_.revoked, False),
                class_.expires_at >= datetime.utcnow()  # noqa
            )
        ).values(revoked=True)
        result = await session.execute(query)
        return result.rowcount

    @staticmethod
    async def _get_token(type_: TokenType, jti: str, session: AsyncSession):
        class_ = get_token_class(type_)
        now = datetime.utcnow()  # noqa
        query = select(class_).where(
            and_(
                eq(class_.jti, jti),
                eq(class_.revoked, False),
                class_.expires_at >= now
            )
        )
        result = await session.execute(query)
        return result.scalars().first()


tokens_service = TokenService(async_session_factory)
