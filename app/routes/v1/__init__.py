from sanic import Blueprint

from .auth import auth
from .client import client
from .token import token
from .business import business

blueprints = (
    auth, client, token, business
)

api_v1 = Blueprint.group(*blueprints, url_prefix='v1')
