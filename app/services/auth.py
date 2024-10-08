from datetime import timedelta, datetime

from app.db import async_session_factory
from app.exceptions import (
    SMSCooldown,
    UserDoesNotExist,
    WrongPassword,
    UserHasNoBusinesses,
    YouAreRetardedError,
)
from app.services.otp import otp_service
from app.tasks import send_sms_to_phone
from app.utils.rand import random_code
from .tokens import tokens_service
from .user import user_service
from .base import BaseService
from ..schemas.enums import Realm


class AuthorizationService(BaseService):
    async def send_otp(
        self,
        phone: str,
        business: str,
        *,
        code_lifetime: timedelta = timedelta(minutes=5),
        sms_cooldown: timedelta = timedelta(seconds=30),
        revoke_old: bool = True,
        sms_limit: int = 10,
        sms_limit_time: timedelta = timedelta(hours=3),
    ) -> str:
        """
        Send a one-time password (OTP) to the specified phone number.

        This method generates and sends an OTP to the provided phone number
        in international format. It includes options for managing the
        lifetime of the code, cooldown periods between SMS messages, and
        limits on the number of messages sent.

        Args:
            phone (str): The phone number to which the OTP will be sent,
                         formatted in international format (e.g., +1234567890).
            business (str): Business code.
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
            str: OTP code if it was successfully sent.

        Raises:
            Exception: If there is an error in sending the OTP, such as
                       exceeding the SMS limit or invalid phone number format.
        """
        now = datetime.utcnow()

        async with self.get_session() as session:
            async with session.begin():
                otp_service_ = otp_service.with_context({"session": session})
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
                otp_instance = await otp_service_.create(
                    phone, code, now, now + code_lifetime
                )
            await session.refresh(otp_instance)
            return code

    async def business_admin_login(self, phone: str, password: str):
        async with self.get_session() as session:
            user = await user_service.with_context(
                {"session": session}
            ).get_user_by_phone_with_cache(phone)
            if not user:
                raise UserDoesNotExist(f"User with phone {phone} does not exists.")
            if not user.businesses:
                raise UserHasNoBusinesses(f"User has no businesses to manage.")
            if user.businesses and not user.password:
                raise YouAreRetardedError("How the fuck user even registered?")
            if not user.check_password(password):
                raise WrongPassword

            token_pair = await tokens_service.with_context(
                {"session": session, "request": self.context["request"]}
            ).create_tokens_for_user(user=user, realm=Realm.web)
        return user, *token_pair


auth_service = AuthorizationService(async_session_factory)
