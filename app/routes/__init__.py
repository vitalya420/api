"""
This module includes all the routes for the application.

It imports and groups the mobile, web, and common API routes into a single
Blueprint for centralized management. The routes are prefixed with "/api"
to indicate that they belong to the application's API.

Modules included:
- mobile_api: Contains routes for the mobile application.
- web_api: Contains routes for the web application.
- common_api: Contains routes that are shared across all versions of the API.
"""

from sanic import Blueprint

from .mobile import mobile_api
from .web import web_api
from .common import common_api

blueprints = (mobile_api, web_api, common_api)

api = Blueprint.group(*blueprints, url_prefix="/api")
