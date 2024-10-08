from sanic import Blueprint

from .mobile import mobile_api
from .web import web_api
from .common import common_api

blueprints = (mobile_api, web_api, common_api)

api = Blueprint.group(*blueprints, url_prefix="/api")
