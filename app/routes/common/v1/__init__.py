from sanic import Blueprint

from .auth import auth
from .tokens import tokens

blueprint = (auth, tokens)

common_v1 = Blueprint.group(*blueprint, url_prefix="/v1")
