from typing import Dict, Union, Callable, Awaitable, Type, Self

from sanic import Request

from app.enums import Realm
from app.models import AccessToken, User, OTP, Business, BusinessClient
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

    token_getter: Callable[..., Awaitable[Union[AccessToken, None]]] = ...
    user_getter: Callable[..., Awaitable[Union[User, None]]] = ...
    business_getter: Callable[..., Awaitable[Union[Business, None]]] = ...
    client_getter: Callable[..., Awaitable[Union[BusinessClient, None]]] = ...

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
            self._access_token = await self.token_getter(
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
                self._user = await self.user_getter(
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
        return await self.business_getter(self.business_code, use_cache=True)

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

    @classmethod
    def set_getters(
        cls,
        token_getter: Callable[..., Awaitable[Union[AccessToken, None]]],
        user_getter: Callable[..., Awaitable[Union[User, None]]],
        business_getter: Callable[..., Awaitable[Union[Business, None]]],
        client_getter: Callable[..., Awaitable[Union[BusinessClient, None]]],
    ) -> Type[Self]:
        """
        Set the getter functions for retrieving access tokens, user information,
        business information, and client information for the ApiRequest class.

        This method allows the ApiRequest class to be configured with specific
        functions that will be used to fetch the necessary data when requested.
        This is particularly useful for avoiding circular imports in services that
        require access to the request class.

        Args:
            token_getter (Callable[..., Awaitable[Union[AccessToken, None]]]):
                A callable that retrieves the access token associated with the request.
            user_getter (Callable[..., Awaitable[Union[User, None]]]):
                A callable that retrieves the user associated with the access token.
            business_getter (Callable[..., Awaitable[Union[Business, None]]]):
                A callable that retrieves the business associated with the request.
            client_getter (Callable[..., Awaitable[Union[BusinessClient, None]]]):
                A callable that retrieves the client associated with the request.

        Returns:
            Type[Self]: The ApiRequest class with the specified getter functions set.

        Example:
            ApiRequest = create_request_class()
            ApiRequest.set_getters(
                 token_getter=my_token_getter,
                 user_getter=my_user_getter,
                 business_getter=my_business_getter,
                 client_getter=my_client_getter
            )
        """
        class_ = cls
        class_.token_getter = token_getter
        class_.user_getter = user_getter
        class_.business_getter = business_getter
        class_.client_getter = client_getter
        return class_
