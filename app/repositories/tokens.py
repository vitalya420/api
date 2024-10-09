from typing import Optional, Tuple

from .base import BaseRepository
from app.models import AccessToken, RefreshToken
from app.schemas.enums import Realm


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
