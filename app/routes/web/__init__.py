from sanic import Blueprint, Forbidden, Unauthorized

from .v1 import web_api_v1
from app.request import ApiRequest
from app.schemas.user import Realm

web_api = Blueprint.group(web_api_v1, url_prefix="/web")


@web_api.middleware("request")  # noqa
async def check_permissions(request: ApiRequest):
    if not request.jwt_payload:
        raise Unauthorized("Access token is not provided")
    if request.realm != Realm.web:
        raise Forbidden
