from sanic import Blueprint

from .mobile import mobile_api
from .web import web_api

from .v1 import api_v1

api = Blueprint.group(api_v1, mobile_api, web_api, url_prefix="/api")
