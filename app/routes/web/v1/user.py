from sanic import Blueprint, json
from sanic_ext.extensions.openapi import openapi

from app.request import ApiRequest
from app.schemas.user import WebUserResponse

user = Blueprint("web-user", url_prefix="/user")


@user.route("/")
@openapi.definition(secured={"token": []})
async def get_user(request: ApiRequest):
    logged_user = await request.get_user()
    return json(WebUserResponse.model_validate(logged_user).model_dump())
