from sanic import Blueprint

from .v1 import common_v1

common_api = Blueprint.group(common_v1, url_prefix="/common")
