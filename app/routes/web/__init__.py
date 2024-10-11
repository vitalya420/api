"""
This module contains all the routes for the web application.

It imports the `web_api_v1` Blueprint, which includes the routes for version 1
of the web API, and groups it under a new Blueprint with the URL prefix "/web".
This structure allows for the organization of web API routes that may be utilized
by the web application.

Modules included:
- web_api_v1: Contains the routes for web API version 1.
"""

from sanic import Blueprint, Forbidden, Unauthorized

from .v1 import web_api_v1
from app.request import ApiRequest
from app.enums import Realm

web_api = Blueprint.group(web_api_v1, url_prefix="/web")


@web_api.middleware("request")  # noqa
async def check_permissions(request: ApiRequest):
    if not request.jwt_payload:
        raise Unauthorized("Access token is not provided")
    if request.realm != Realm.web:
        raise Forbidden
