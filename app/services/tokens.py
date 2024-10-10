from typing import Union, Optional

from sanic import Request

from app.base import BaseService
from app.db import async_session_factory
from app.models import AccessToken
from app.repositories.tokens import TokensRepository
from app.schemas.user import Realm


class TokenService(BaseService):
    __repository_class__ = TokensRepository

    async def create_tokens(
        self,
        user_id: int,
        request: Request,
        realm: Realm,
        business_code: Optional[str] = None,
    ):
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


tokens_service = TokenService(async_session_factory)
