from sanic import Blueprint

from .auth import auth

blueprint = (auth,)

common_v1 = Blueprint.group(*blueprint, url_prefix="/v1")
