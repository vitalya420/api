from sanic import Blueprint

from .analytics import analytics

api_v2 = Blueprint.group(analytics, url_prefix='/v2')
