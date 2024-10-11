"""
This module contains routes for the mobile app across all versions of the API.

It imports the `mobile_api_v1` Blueprint, which includes the routes for version 1,
and groups it under a new Blueprint with the URL prefix "/mobile". This structure
facilitates the organization of mobile API routes that may span multiple versions.

Modules included:
- mobile_api_v1: Contains the routes for mobile API version 1.
"""

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
