from sanic import Blueprint, json

from app.request import ApiRequest

user = Blueprint("web-user", url_prefix="/user")


@user.route("/")
async def get_user(request: ApiRequest):
    return json(
        {
            "ok": True,
            "message": "This route returns information about user, his permissions",
        }
    )
