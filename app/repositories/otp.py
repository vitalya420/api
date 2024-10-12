from datetime import datetime
from typing import Union, Sequence

from sqlalchemy import select, and_, update

from app.base import BaseRepository
from app.repositories.business import BusinessRepository
from app.exceptions import BusinessDoesNotExist
from app.models import OTP
from app.enums import Realm


class OTPRepository(BaseRepository):
    """
    Repository class for managing One-Time Password (OTP) related database operations.

    This class provides methods to create, revoke, and retrieve OTP entities from the database.
    It extends the BaseRepository to leverage common database functionalities.
    """

    async def create(
        self,
        phone: str,
        realm: Realm,
        business_code: str,
        code: str,
        sent_at: datetime,
        expiration: datetime,
    ):
        """
        Create a new OTP instance.

        This method initializes a new OTP instance with the provided details and associates
        it with the specified business. If the business does not exist, a BusinessDoesNotExist
        exception is raised.

        Args:
            phone (str): The phone number to which the OTP is sent.
            realm (Realm): The realm associated with the OTP.
            business_code (str): The code of the business associated with the OTP.
            code (str): The OTP code to be sent.
            sent_at (datetime): The timestamp when the OTP was sent.
            expiration (datetime): The timestamp when the OTP expires.

        Returns:
            OTP: The newly created OTP instance.

        Raises:
            BusinessDoesNotExist: If the business with the given code does not exist.
        """
        if (
            business := await BusinessRepository(self.session).get_business(
                business_code
            )
        ) is None:
            raise BusinessDoesNotExist(
                f"Business with code {business_code} does not exist"
            )

        instance = OTP(
            phone=phone,
            realm=realm,
            business_code=business_code,
            code=code,
            sent_at=sent_at,
            expires_at=expiration,
        )
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def revoke_otps(self, phone: str, business_code: str) -> int:
        """
        Revoke all un-used and un-revoked OTPs for a given phone number and business code.

        This method updates the status of OTPs to revoked for the specified phone number
        and business code, ensuring that only OTPs that have not been used or revoked are affected.

        Args:
            phone (str): The phone number associated with the OTPs to revoke.
            business_code (str): The code of the business associated with the OTPs to revoke.

        Returns:
            int: The number of OTPs that were revoked.
        """
        query = (
            update(OTP)
            .where(
                and_(
                    OTP.phone == phone,
                    OTP.business_code == business_code,
                    OTP.revoked.is_(False),
                    OTP.used.is_(False),
                )
            )
            .values(revoked=True)
        )
        result = await self.session.execute(query)
        return result.rowcount  # noqa

    async def get_unexpired_otp(
        self, phone: str, business_code: str
    ) -> Union[OTP, None]:
        """
        Retrieve an unexpired OTP for a given phone number and business code.

        This method queries the database for an OTP that has not expired, is not revoked,
        and has not been used.

        Args:
            phone (str): The phone number associated with the OTP.
            business_code (str): The code of the business associated with the OTP.

        Returns:
            Union[OTP, None]: The unexpired OTP instance if found, or None if not found.
        """
        query = select(OTP).where(
            and_(
                OTP.phone == phone,
                OTP.business_code == business_code,
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
        """
        Retrieve all OTPs sent to a given phone number for a specific business code after a certain expiration time.

        This method queries the database for OTPs that were sent to the specified phone number
        and business code, filtering by the sent timestamp to ensure only relevant OTPs are returned.

        Args:
            phone (str): The phone number associated with the OTPs.
            business_code (str): The code of the business associated with the OTPs.
            expiration (datetime): The timestamp to filter OTPs sent after this time.

        Returns:
            Sequence[OTP]: A list of OTP instances that match the criteria.
        """
        query = select(OTP).where(
            and_(
                OTP.phone == phone,
                OTP.business_code == business_code,
                OTP.expires_at <= expiration,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def set_code_used(self, pk: int):
        """
        Mark an OTP as used based on its primary key.

        This method updates the status of the specified OTP to indicate that it has been used.

        Args:
            pk (int): The primary key of the OTP to mark as used.

        Returns:
            int: The number of OTPs that were updated (should be 1 if the OTP exists).
        """
        query = update(OTP).where(OTP.id == pk).values(used=True)
        result = await self.session.execute(query)
        return result.rowcount
