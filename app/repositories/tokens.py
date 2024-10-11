from datetime import datetime
from typing import Optional, Tuple, TypeVar, Type

from sqlalchemy import select, and_, update
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.operators import eq

from app.base import BaseRepository
from app.exceptions import BusinessCodeNotProvided, RefreshTokenNotFound
from app.models import AccessToken, RefreshToken
from app.enums import Realm

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
        if class_ is RefreshToken:
            query = query.options(joinedload(class_.access_token))
        elif class_ is AccessToken:
            query = query.options(joinedload(class_.refresh_token))
        res = await self.session.execute(query)
        return res.scalars().first()

    async def revoke_token(self, class_: Type[T], jti: str):
        if (token := await self.get_token(class_, jti)) is not None:
            token.revoked = True

    async def get_tokens(self, user_id: int, realm: Realm, business_code: str):
        and_clause = and_(
            AccessToken.user_id == user_id,
            AccessToken.realm == realm,
        )

        if realm == Realm.mobile:
            if business_code is None:
                raise BusinessCodeNotProvided(
                    "For mobile app business id should be provided."
                )
            eq_ = eq(AccessToken.business_code, business_code)
            and_clause = and_(and_clause, eq(AccessToken.business_code, business_code))
        query = select(AccessToken).where(and_clause)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def refresh_revoke(
            self, refresh_jti: str
    ) -> Tuple[AccessToken, RefreshToken]:
        refresh_token = await self.get_token(RefreshToken, refresh_jti)
        if refresh_token is None:
            raise RefreshTokenNotFound(
                f"Active refresh token with jti {refresh_jti} not found."
            )
        refresh_token.revoked = True
        refresh_token.access_token.revoked = True
        return refresh_token.access_token, refresh_token
