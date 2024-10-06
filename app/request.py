from typing import Dict, Union

from sanic import Request

from app.models import AccessToken, User
from app.utils.lazy import create_lazy_services_factory
from app.utils.tokens import decode_token
from app.services import tokens_service, user_service


class ApiRequest(Request):
    def __init__(self, *sanic_args, **sanic_kwargs):
        super().__init__(*sanic_args, **sanic_kwargs)
        self.services = create_lazy_services_factory(context={'request': self})

        self._business_code: Union[str, None] = None
        self._jwt_payload: Union[Dict[str, Union[str, int, bool]], None] = None
        self._access_token: Union[AccessToken, None] = None
        self._user: Union[User, None] = None

    async def get_access_token(self) -> Union[AccessToken, None]:
        if (self._access_token is None
                and self.jwt_payload is not None
                and self.jwt_payload.get('type', '') == 'access'):
            self._access_token = await tokens_service.get_access_token_with_cache(self.jwt_payload['jti'])
        return self._access_token

    async def get_user(self) -> Union[User, None]:
        if self._user is None:
            access_token = await self.get_access_token()
            if access_token:
                self._user = await user_service.get_user_by_id_with_cache(access_token.user_id)
        return self._user

    @property
    def jwt_payload(self):
        if self._jwt_payload is None:
            if self.token:
                self._jwt_payload = decode_token(self.token)
        return self._jwt_payload

    @property
    def business_code(self):
        """If access token is provided then return business code from it"""
        if self._access_token:
            self._business_code = self._access_token.business
        elif self._business_code is None:
            self._business_code = self.headers.get('X-Business-ID')
        return self._business_code
