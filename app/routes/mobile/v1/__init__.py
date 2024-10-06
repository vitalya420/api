from sanic import Blueprint

from .client import client
from .business import business

blueprints = (client, business)

mobile_api_v1 = Blueprint.group(*blueprints, url_prefix="v1")
