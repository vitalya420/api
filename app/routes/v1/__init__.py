from sanic import Blueprint

from .auth import auth
from .token import token
from .business import business

blueprints = (auth, token)

api_v1 = Blueprint.group(*blueprints, url_prefix="v1")
