from datetime import datetime
from typing import Union

from app.db import async_session_factory
from app.models import OTP
from app.repositories.otp import OTPRepository
from app.base import BaseService
from app.enums import Realm


class OTPService(BaseService):
    __repository_class__ = OTPRepository

    async def get_unexpired_otp(self, phone: str, business_code: str):
        async with self.get_repo() as otp_repo:
            return await otp_repo.get_unexpired_otp(phone, business_code)

    async def get_otps(self, phone: str, business_code: str, expiration: datetime):
        async with self.get_repo() as otp_repo:
            return await otp_repo.get_otps(phone, business_code, expiration)

    async def revoke_otps(self, phone: str, business_code: str):
        async with self.get_repo() as otp_repo:
            return await otp_repo.revoke_otps(phone, business_code)

    async def create(
        self,
        phone: str,
        realm: Realm,
        business_code: str,
        code: str,
        sent_at: datetime,
        expiration: datetime,
    ):
        async with self.get_repo() as otp_repo:
            return await otp_repo.create(
                phone, realm, business_code, code, sent_at, expiration
            )

    async def set_code_used(self, otp_or_pk: Union[OTP, int]):
        pk = otp_or_pk.id if isinstance(otp_or_pk, OTP) else otp_or_pk
        async with self.get_repo() as otp_repo:
            return await otp_repo.set_code_used(pk)


otp_service = OTPService(async_session_factory)
