import asyncio
from typing import Union, Optional, Tuple

from sanic import Request

from app.base import BaseService
from app.db import async_session_factory
from app.models import AccessToken, Business, RefreshToken
from app.repositories.tokens import TokensRepository
from app.schemas.user import User
from app.enums import Realm
from app.utils import force_id, force_code


class TokenService(BaseService):
    __repository_class__ = TokensRepository

    async def create_tokens(
        self,
        user_id: int,
        request: Request,
        realm: Realm,
        business_code: Optional[str] = None,
    ) -> Tuple[AccessToken, RefreshToken]:
        async with self.get_repo() as repo:
            return await repo.create_tokens(
                user_id,
                realm,
                business_code,
                request.headers.get("X-Real-IP", "<no ip>"),
                request.headers.get("User-Agent", "<no user agent>"),
            )

    async def get_access_token(
        self, jti: str, alive_only: bool = True, use_cache: bool = True
    ) -> Union[AccessToken, None]:
        async with self.get_repo() as token_repo:
            if use_cache:
                return await self.with_cache(
                    AccessToken, jti, token_repo.get_token, AccessToken, jti, alive_only
                )
            return await token_repo.get_token(AccessToken, jti, alive_only)

    async def list_user_issued_tokens(
        self, user: Union[User, int], realm: Realm, business: Union[Business, str, None]
    ):
        async with self.get_repo() as token_repo:
            return await token_repo.get_tokens(
                force_id(user),
                realm,
                force_code(business) if business is not None else None,
            )

    async def refresh_tokens(
        self, refresh_jti: str, request: Request
    ) -> Tuple[AccessToken, RefreshToken]:
        async with self.get_repo() as tokens_repo:
            # Revoke access and refresh tokens
            # And delete it from cache
            access, refresh = await tokens_repo.refresh_revoke(refresh_jti)

            await asyncio.gather(
                self.cache_delete_object(access), self.cache_delete_object(refresh)
            )
            return await self.reuse_session().create_tokens(
                user_id=access.user_id,
                request=request,
                realm=access.realm,
                business_code=access.business_code,
            )

    async def revoke_access_token(self, access_token: AccessToken):
        async with self.get_repo() as tokens_repo:
            await tokens_repo.revoke_token(AccessToken, access_token.jti)
            await asyncio.gather(
                self.cache_delete_object(access_token),
                self.cache_delete_object(access_token.refresh_token),
            )

    async def user_revokes_access_token_by_jti(
        self, user: Union[User, int], jti: str
    ) -> Union[Tuple[AccessToken, RefreshToken], None]:
        async with self.get_repo() as tokens_repo:
            access = await tokens_repo.get_token(AccessToken, jti)
            if access is not None and access.user_id == force_id(user):
                access.revoked = True
                access.refresh_token.revoked = True
                await asyncio.gather(
                    self.cache_delete_object(access),
                    self.cache_delete_object(access.refresh_token),
                )
                return access, access.refresh_token


tokens_service = TokenService(async_session_factory)
