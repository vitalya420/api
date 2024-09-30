from sanic import Blueprint

from .v1 import api_v1
from .v2 import api_v2

api = Blueprint.group(api_v1, api_v2, url_prefix='/api')

