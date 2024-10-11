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
        """
        Retrieve an unexpired OTP for a given phone number and business code.

        This method queries the repository for an OTP that has not yet expired
        for the specified phone number and business code.

        Args:
            phone (str): The phone number associated with the OTP, formatted in international format (e.g., +1234567890).
            business_code (str): The unique code of the business associated with the OTP.

        Returns:
            Union[OTP, None]: The unexpired OTP instance if found, or None if not found.
        """
        async with self.get_repo() as otp_repo:
            return await otp_repo.get_unexpired_otp(phone, business_code)

    async def get_otps(self, phone: str, business_code: str, expiration: datetime):
        """
        Retrieve all OTPs for a given phone number and business code up to a specified expiration time.

        This method queries the repository for all OTPs associated with the specified
        phone number and business code that are valid until the provided expiration time.

        Args:
            phone (str): The phone number associated with the OTPs, formatted in international format (e.g., +1234567890).
            business_code (str): The unique code of the business associated with the OTPs.
            expiration (datetime): The expiration time to filter the OTPs.

        Returns:
            List[OTP]: A list of OTP instances that match the criteria.
        """
        async with self.get_repo() as otp_repo:
            return await otp_repo.get_otps(phone, business_code, expiration)

    async def revoke_otps(self, phone: str, business_code: str):
        """
        Revoke all OTPs associated with a given phone number and business code.

        This method marks all OTPs for the specified phone number and business code
        as revoked, making them unusable.

        Args:
            phone (str): The phone number associated with the OTPs, formatted in international format (e.g., +1234567890).
            business_code (str): The unique code of the business associated with the OTPs.

        Returns:
            None: This method does not return a value.
        """
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
    ) -> OTP:
        """
        Create a new OTP and store it in the repository.

        This method generates a new OTP for the specified phone number and business code,
        and stores it along with its creation time and expiration time.

        Args:
            phone (str): The phone number to which the OTP will be sent, formatted in international format (e.g., +1234567890).
            realm (Realm): The realm indicating the context in which the OTP is used (e.g., web or mobile).
            business_code (str): The unique code of the business associated with the OTP.
            code (str): The OTP code to be stored.
            sent_at (datetime): The timestamp when the OTP was sent.
            expiration (datetime): The timestamp when the OTP will expire.

        Returns:
            OTP: The newly created OTP instance.
        """
        async with self.get_repo() as otp_repo:
            return await otp_repo.create(
                phone, realm, business_code, code, sent_at, expiration
            )

    async def set_code_used(self, otp_or_pk: Union[OTP, int]):
        """
        Mark an OTP code as used.

        This method updates the status of the specified OTP to indicate that it has been used.
        The OTP can be provided as an instance or by its primary key.

        Args:
            otp_or_pk (Union[OTP, int]): The OTP instance or the primary key of the OTP to be marked as used.

        Returns:
            None: This method does not return a value.
        """
        pk = otp_or_pk.id if isinstance(otp_or_pk, OTP) else otp_or_pk
        async with self.get_repo() as otp_repo:
            return await otp_repo.set_code_used(pk)


otp_service = OTPService(async_session_factory)
