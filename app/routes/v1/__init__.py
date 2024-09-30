from sanic import Blueprint
from .user import user

api_v1 = Blueprint.group(user, version=1)
