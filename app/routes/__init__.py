from sanic import Blueprint

from .v1 import api_v1
from .gateway import gateway

api = Blueprint.group(api_v1, url_prefix="/api")
