from datetime import timedelta, datetime

from app.db import async_session_factory
from app.exceptions import SMSCooldown
from app.services.otp import otp_service
from app.tasks import send_sms_to_phone
from app.utils.rand import random_code
from .base import BaseService


class AuthorizationService(BaseService):
    async def send_otp(self,
                       phone: str,
                       *,
                       code_lifetime: timedelta = timedelta(minutes=5),
                       sms_cooldown: timedelta = timedelta(seconds=1),
                       revoke_old: bool = True,
                       sms_limit: int = 10,
                       sms_limit_time: timedelta = timedelta(hours=3)):
        """
        Send a one-time password (OTP) to the specified phone number.

        This method generates and sends an OTP to the provided phone number
        in international format. It includes options for managing the
        lifetime of the code, cooldown periods between SMS messages, and
        limits on the number of messages sent.

        Args:
            phone (str): The phone number to which the OTP will be sent,
                         formatted in international format (e.g., +1234567890).
            code_lifetime (timedelta, optional): The duration for which the
                                                  OTP is valid. Defaults to
                                                  5 minutes.
            sms_cooldown (timedelta, optional): The minimum time that must
                                                 elapse between consecutive
                                                 SMS messages sent to the
                                                 same phone number. Defaults
                                                 to 30 seconds.
            revoke_old (bool, optional): If set to True, any previously sent
                                          OTPs will be invalidated, making
                                          them unusable. Defaults to True.
            sms_limit (int, optional): The maximum number of SMS messages
                                        that can be sent to the specified
                                        phone number within the time frame
                                        defined by `sms_limit_time`. Defaults
                                        to 5.
            sms_limit_time (timedelta, optional): The time period during which
                                                   the `sms_limit` applies.
                                                   Defaults to 3 hours.

        Returns:
            None: If the OTP is successfully sent.

        Raises:
            Exception: If there is an error in sending the OTP, such as
                       exceeding the SMS limit or invalid phone number format.
        """
        now = datetime.utcnow()

        async with self.get_session() as session:
            async with session.begin():
                otp_service_ = otp_service.with_context({'session': session})
                # Check is cooldown has passed
                existing_otp = await otp_service_.get_otp(phone, now - sms_cooldown)
                if existing_otp:
                    raise SMSCooldown("Too many SMS")

                # Check for limit
                limit_result = await otp_service_.get_otp(phone, now - sms_limit_time)
                sms_count = len(limit_result)
                if sms_count >= sms_limit:
                    raise SMSCooldown("Too many SMS")

                if revoke_old:
                    row_affected = await otp_service_.revoke_otps(phone)

                code = random_code()
                await send_sms_to_phone(phone, code)
                otp_instance = await otp_service_.create(phone, code, now, now + code_lifetime)
            await session.refresh(otp_instance)


auth_service = AuthorizationService(async_session_factory)
