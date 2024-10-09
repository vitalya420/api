from datetime import datetime
from typing import Optional, Tuple, TypeVar, Union, Type

from sqlalchemy import select, and_

from app.base import BaseRepository
from app.models import AccessToken, RefreshToken
from app.schemas.enums import Realm

T = TypeVar("T", AccessToken, RefreshToken)


class TokensRepository(BaseRepository):
    async def create_tokens(
        self,
        user_id: int,
        realm: Realm,
        business_code: Optional[str] = None,
        ip_address: Optional[str] = "<no ip>",
        user_agent: Optional[str] = "<no user agent>",
    ) -> Tuple[AccessToken, RefreshToken]:
        refresh_token = RefreshToken(
            user_id=user_id,
            realm=realm,
            business_code=business_code,
        )
        self.session.add(refresh_token)
        await self.session.flush()

        access_token = AccessToken(
            user_id=user_id,
            realm=realm,
            business_code=business_code,
            ip_addr=ip_address,
            user_agent=user_agent,
            refresh_token_jti=refresh_token.jti,
        )
        self.session.add(access_token)
        await self.session.flush()
        return access_token, refresh_token

    async def get_token(self, class_: Type[T], jti: str, alive_only: bool = True) -> T:
        query = select(class_).where(class_.jti == jti)  # noqa
        if alive_only:
            query = query.where(
                and_(class_.revoked == False, class_.expires_at >= datetime.utcnow())
            )
        res = await self.session.execute(query)
        return res.scalars().first()
