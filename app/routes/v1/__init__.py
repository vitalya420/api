from sanic import Blueprint

from .auth import auth
from .client import client
from .token import token

blueprints = (
    auth, client, token
)

api_v1 = Blueprint.group(*blueprints, url_prefix='v1')