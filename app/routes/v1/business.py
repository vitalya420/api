from sanic import Blueprint
from sanic.request import Request

from app.exceptions import EndpointDoNothing

business = Blueprint('business', url_prefix='/business')


@business.route("/")
async def index(request: Request):
    raise EndpointDoNothing
