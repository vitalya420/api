from typing import Dict, Union

from sanic import Request

from app.models import AccessToken, User, OTP, Business
from app.enums import Realm
from app.services import tokens_service, user_service, business_service
from app.utils.tokens import decode_token


class ApiRequest(Request):
    """
    Custom API request class that extends the Sanic Request.

    This class adds additional context and functionality for handling API requests,
    including managing access tokens, user information, business context, and OTP.

    Attributes:
        otp_context (Union[OTP, None]): The OTP context associated with the request.
        _business_code (Union[str, None]): The business code extracted from the access token.
        _jwt_payload (Union[Dict[str, Union[str, int, bool]], None]): The decoded JWT payload.
        _access_token (Union[AccessToken, None]): The access token associated with the request.
        _user (Union[User, None]): The user associated with the access token.
    """

    def __init__(self, *sanic_args, **sanic_kwargs):
        """
        Initialize the ApiRequest instance.

        Args:
            *sanic_args: Positional arguments passed to the Sanic Request constructor.
            **sanic_kwargs: Keyword arguments passed to the Sanic Request constructor.
        """
        super().__init__(*sanic_args, **sanic_kwargs)
        self.otp_context: Union[OTP, None] = None

        self._business_code: Union[str, None] = None
        self._jwt_payload: Union[Dict[str, Union[str, int, bool]], None] = None
        self._access_token: Union[AccessToken, None] = None
        self._user: Union[User, None] = None

    async def get_access_token(self) -> Union[AccessToken, None]:
        """
        Retrieve the access token associated with the request.

        If the access token is not already retrieved, it will be fetched using the
        JWT payload's JTI (JWT ID).

        Returns:
            Union[AccessToken, None]: The access token if found, or None if not found.
        """
        if (
            self._access_token is None
            and self.jwt_payload is not None
            and self.jwt_payload.get("type", "") == "access"
        ):
            self._access_token = await tokens_service.get_access_token(
                self.jwt_payload["jti"], use_cache=True
            )
        return self._access_token

    async def get_user(self) -> Union[User, None]:
        """
        Retrieve the user associated with the access token.

        If the user is not already retrieved, it will be fetched using the user ID
        from the access token.

        Returns:
            Union[User, None]: The user if found, or None if not found.
        """
        if self._user is None:
            access_token = await self.get_access_token()
            if access_token:
                self._user = await user_service.get_user(
                    pk=access_token.user_id, use_cache=True
                )
        return self._user

    async def get_business(self) -> Union[Business, None]:
        """
        Retrieve the business associated with the request.

        If the business code is not set, None will be returned. Otherwise, the business
        will be fetched using the business code.

        Returns:
            Union[Business, None]: The business if found, or None if not found.
        """
        if self.business_code is None:
            return None
        return await business_service.get_business(self.business_code, use_cache=True)

    def set_otp_context(self, otp: OTP):
        """
        Set the OTP context for the request.

        Args:
            otp (OTP): The OTP context to associate with the request.
        """
        self.otp_context = otp

    @property
    def jwt_payload(self) -> Union[Dict[str, Union[str, int, bool]], None]:
        """
        Get the decoded JWT payload from the access token.

        If the JWT payload is not already decoded, it will be decoded from the token.

        Returns:
            Union[Dict[str, Union[str, int, bool]], None]: The decoded JWT payload, or None if not available.
        """
        if self._jwt_payload is None:
            if self.token:
                self._jwt_payload = decode_token(self.token)
        return self._jwt_payload

    @property
    def business_code(self) -> Union[str, None]:
        """
        Get the business code from the access token.

        If the access token is provided, the business code will be extracted from it.

        Returns:
            Union[str, None]: The business code if available, or None if not.
        """
        if self._access_token:
            self._business_code = self._access_token.business_code
        return self._business_code

    @property
    def realm(self) -> Union[Realm, None]:
        """
        Get the realm from the JWT payload.

        If the JWT payload contains a realm, it will be returned as an instance of the
        Realm enum.

        Returns:
            Union[Realm, None]: The realm if available, or None if not found.
        """
        if self.jwt_payload and self.jwt_payload.get("realm"):
            return Realm(self.jwt_payload["realm"])
