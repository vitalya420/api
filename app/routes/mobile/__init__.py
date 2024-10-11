from sanic import Blueprint, Unauthorized, Forbidden

from .v1 import mobile_api_v1
from app.request import ApiRequest
from app.enums import Realm

mobile_api = Blueprint.group(mobile_api_v1, url_prefix="/mobile")


@mobile_api.middleware("request")  # noqa
async def check_permissions(request: ApiRequest):
    if not request.jwt_payload:
        raise Unauthorized("Access token is not provided")
    if request.realm != Realm.mobile:
        raise Forbidden
