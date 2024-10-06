from sanic import Blueprint

from .user import user
from .business import business

blueprints = (user, business)

web_api_v1 = Blueprint.group(*blueprints, url_prefix="/v1")
