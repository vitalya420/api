from datetime import datetime
from typing import Union

from sqlalchemy import select, and_, update
from sqlalchemy.sql.operators import eq

from .base import BaseService
from app.models import OTP
from app.db import async_session_factory


class OTPService(BaseService):
    async def get_unexpired_otp(self, phone: str):
        now = datetime.utcnow()

        query = select(OTP).where(
            and_(
                OTP.destination == phone,
                OTP.expires_at > now,
                OTP.revoked.is_(False),
                OTP.used.is_(False)
            )
        )

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def get_otp(self, phone: str, expiration: datetime):
        query = select(OTP).where(
            and_(
                OTP.destination == phone,
                OTP.sent_at >= expiration,
            )
        )
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def revoke_otps(self, phone: str):
        query = update(OTP).where(
            and_(
                eq(OTP.destination, phone),
                eq(OTP.revoked, False),
                eq(OTP.used, False)
            )
        ).values(revoked=True)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.rowcount

    async def create(self, phone: str, code: str, sent_at: datetime, expiration: datetime):
        instance = OTP(destination=phone, code=code, sent_at=sent_at, expires_at=expiration)
        async with self.get_session() as session:
            session.add(instance)
            return instance

    async def set_code_used(self, otp_or_pk: Union[OTP, int]):
        pk = otp_or_pk.id if isinstance(otp_or_pk, OTP) else otp_or_pk
        query = update(OTP).where(OTP.id == pk).values(used=True)
        async with self.get_session() as session:
            result = await session.execute(query)
            return result.rowcount


otp = OTPService(async_session_factory)
