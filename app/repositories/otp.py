from datetime import datetime
from typing import Union, Sequence

from sqlalchemy import select, and_, update

from app.base import BaseRepository
from .business import BusinessRepository
from app.exceptions import BusinessDoesNotExist
from app.models import OTP
from app.enums import Realm


class OTPRepository(BaseRepository):
    async def create(
        self,
        phone: str,
        realm: Realm,
        business_code: str,
        code: str,
        sent_at: datetime,
        expiration: datetime,
    ):
        if (
            business := await BusinessRepository(self.session).get_business(
                business_code
            )
        ) is None:
            raise BusinessDoesNotExist(
                f"Business with code {business_code} does not exist"
            )

        instance = OTP(
            destination=phone,
            realm=realm,
            business=business_code,
            code=code,
            sent_at=sent_at,
            expires_at=expiration,
        )
        self.session.add(instance)
        return instance

    async def revoke_otps(self, phone: str, business_code: str) -> int:
        query = (
            update(OTP)
            .where(
                and_(
                    OTP.destination == phone,
                    OTP.business == business_code,
                    OTP.revoked == False,
                    OTP.used == False,
                )
            )
            .values(revoked=True)
        )
        result = await self.session.execute(query)
        return result.rowcount  # noqa

    async def get_unexpired_otp(
        self, phone: str, business_code: str
    ) -> Union[OTP, None]:
        query = select(OTP).where(
            and_(
                OTP.destination == phone,
                OTP.business == business_code,
                OTP.expires_at > datetime.utcnow(),  # noqa
                OTP.revoked.is_(False),
                OTP.used.is_(False),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_otps(
        self, phone: str, business_code: str, expiration: datetime
    ) -> Sequence[OTP]:
        query = select(OTP).where(
            and_(
                OTP.destination == phone,
                OTP.business == business_code,
                OTP.sent_at >= expiration,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def set_code_used(self, pk: int):
        query = update(OTP).where(OTP.id == pk).values(used=True)
        result = await self.session.execute(query)
        return result.rowcount
