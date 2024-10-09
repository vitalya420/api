from sanic import Blueprint, json, BadRequest
from sanic_ext import validate, serializer
from sanic_ext.extensions.openapi import openapi

from app import ApiRequest
from app.exceptions import (
    WrongPassword,
    UserHasNoBusinesses,
    UserDoesNotExist,
    YouAreRetardedError,
)
from app.schemas import SuccessResponse
from app.schemas.auth import AuthRequest, AuthConfirmRequest
from app.schemas.enums import Realm
from app.security import otp_context_required
from app.serializers import serialize_token_pair, serialize_pydantic
from app.serializers.user import serialize_web_user
from app.services import auth_service, otp_service, user_service, tokens_service

auth = Blueprint("auth", url_prefix="/auth")


@auth.post("/confirm")
@openapi.definition(
    body={
        "application/json": AuthConfirmRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
)
@validate(AuthConfirmRequest)
@otp_context_required
async def confirm_auth(request: ApiRequest, body: AuthConfirmRequest):
    print(request.otp_context)
    if request.otp_context:
        if request.otp_context.code == body.otp:
            await otp_service.set_code_used(request.otp_context)
            user = await user_service.get_or_create(request.otp_context.destination)
            tokens = await tokens_service.create_tokens(
                user.id,
                request=request,
                realm=request.otp_context.realm,
                business_code=request.otp_context.business,
            )
            return json(serialize_token_pair(*tokens))
        return BadRequest("Wrong otp code.")
    raise BadRequest


@auth.post("/")
@openapi.definition(
    body={
        "application/json": AuthRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
)
@serializer(serialize_pydantic)
@validate(AuthRequest)
async def authorization(request: ApiRequest, body: AuthRequest):
    if not body.password and body.realm == Realm.web:
        raise BadRequest("Authorization in WEB requires password.")
    if not body.business and body.realm == Realm.mobile:
        raise BadRequest("Authorization in mobile app requires business code.")

    if body.realm == Realm.web:
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

    elif body.realm == Realm.mobile:
        await auth_service.send_otp(body.phone, body.realm, body.business)
        return SuccessResponse(message="OTP sent successfully.")

    return json({"ok": True})
