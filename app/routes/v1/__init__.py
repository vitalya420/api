from sanic import Blueprint

from .user import user
from .business import business
from .token import token

api_v1 = Blueprint.group(user, business, token, url_prefix='v1')
