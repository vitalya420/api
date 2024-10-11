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
from app.utils import random_code
from app.services.tokens import tokens_service
from app.services.user import user_service
from app.base import BaseService
from app.enums import Realm


class AuthorizationService(BaseService):
    async def send_otp(
        self,
        phone: str,
        realm: Realm,
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
            realm (Realm): realm web or mobile.
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
        now = datetime.utcnow()  # noqa

        async with self.get_session() as session:
            otp_service_ = otp_service.with_context({"session": session})
            if existing_otps := await otp_service_.get_otps(
                phone, business, now - sms_cooldown
            ):
                raise SMSCooldown("Too many SMS")
            limit_result = await otp_service_.get_otps(
                phone, business, now - sms_limit_time
            )
            if len(limit_result) >= sms_limit:
                raise SMSCooldown("Too many SMS")
            if revoke_old:
                await otp_service_.revoke_otps(phone, business)
            code = random_code()
            await otp_service_.create(
                phone, realm, business, code, now, now + code_lifetime
            )
            await send_sms_to_phone(phone, code)
        return code

    async def business_admin_login(self, phone: str, password: str):
        """
        Authenticate a business admin user using their phone number and password.

        This method retrieves the user associated with the provided phone number,
        checks if the user exists and has businesses, verifies the password, and
        generates authentication tokens if the login is successful.

        Args:
            phone (str): The phone number of the user attempting to log in,
                         formatted in international format (e.g., +1234567890).
            password (str): The password provided by the user for authentication.

        Returns:
            Tuple[User, str, str]: A tuple containing the authenticated User instance
                                    and the generated access and refresh tokens.

        Raises:
            UserDoesNotExist: If no user is found with the provided phone number.
            UserHasNoBusinesses: If the user does not have any businesses to manage.
            YouAreRetardedError: If the user is registered without a password.
            WrongPassword: If the provided password does not match the user's password.
        """
        async with self.get_session() as session:
            user = await user_service.with_context({"session": session}).get_user(
                phone=phone, use_cache=False
            )
            if not user:
                raise UserDoesNotExist(f"User with phone {phone} does not exists.")
            if not user.businesses:
                raise UserHasNoBusinesses(f"User has no businesses to manage.")
            if user.businesses and not user.password:
                raise YouAreRetardedError("How the fuck user even registered?")
            if not user.check_password(password):
                raise WrongPassword

            token_pair = await tokens_service.with_context(
                {"session": session}
            ).create_tokens(user.id, self.context["request"], Realm.web)
        return user, *token_pair


auth_service = AuthorizationService(async_session_factory)
