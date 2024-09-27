from sanic import Blueprint

from .user import user
from .business import business

api = Blueprint.group(user, business, url_prefix='/api')

