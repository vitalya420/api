from sanic import Blueprint

from .v1 import web_api_v1
from app.request import ApiRequest

web_api = Blueprint.group(web_api_v1, url_prefix="/web")


@web_api.middleware("request")
async def check_permissions(request: ApiRequest):
    pass
