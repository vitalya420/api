from sanic import Blueprint, json, BadRequest
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app import ApiRequest
from app.exceptions import (
    WrongPassword,
    UserHasNoBusinesses,
    UserDoesNotExist,
    YouAreRetardedError,
)
from app.schemas.auth import AuthRequest
from app.schemas.enums import Realm
from app.serializers.user import serialize_web_user
from app.services import auth_service

auth = Blueprint("auth", url_prefix="/auth")


@auth.post("/")
@openapi.definition(
    body={
        "application/json": AuthRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
)
@validate(AuthRequest)
async def authorization(request: ApiRequest, body: AuthRequest):
    if not body.password and body.realm == Realm.web:
        raise BadRequest("Authorization in WEB requires password.")
    if not body.business and body.realm == Realm.mobile:
        raise BadRequest("Authorization in mobile app requires business code.")

    if Realm.web:
        try:
            user, access, refresh = await auth_service.with_context(
                {"request": request}
            ).business_admin_login(body.phone, body.password)
            return json(serialize_web_user(user, access, refresh))
        except (
            WrongPassword,
            UserHasNoBusinesses,
            UserDoesNotExist,
            YouAreRetardedError,
        ):
            raise BadRequest("Wrong phone or password.")
    return json({"ok": True})
