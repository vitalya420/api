from sanic import Blueprint, json

from app import ApiRequest

business = Blueprint("web-business", url_prefix="/business")


@business.get("/")
async def get_business(request: ApiRequest):
    return json({"ok": True, "message": "Returns stats about business"})
