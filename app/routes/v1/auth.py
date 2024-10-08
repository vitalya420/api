"""
This module contains the routes for the authentication endpoints.

It provides endpoints to:
- Request an authentication code (OTP) via SMS.
- Confirm the OTP and issue JWT access and refresh tokens.

Endpoints:
- POST /auth/            : Send an SMS with an OTP for authentication.
- POST /auth/confirm     : Verify the OTP and issue tokens upon successful verification.
"""

from http import HTTPStatus

from sanic import Blueprint, json, BadRequest
from sanic_ext import validate, serializer
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app import ApiRequest
from app.schemas import UserCreate, SuccessResponse
from app.schemas.tokens import TokenPair
from app.schemas.user import UserCodeConfirm
from app.security import rules, otp_context_required
from app.serializers import serialize_token_pair, serialize_pydantic
from app.services import auth_service, otp_service, tokens_service, user_service

auth = Blueprint("auth", url_prefix="/auth")


@auth.post("/")
@openapi.definition(
    body={
        "application/json": UserCreate.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    description="Request an OTP code to phone number. Then proceed with `/api/v1/confirm`",
    summary="Start authorization flow",
    response=[
        Response(
            {
                "application/json": SuccessResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            },
            status=HTTPStatus.OK,
        )
    ],
)
@serializer(serialize_pydantic)
@validate(UserCreate)
async def request_auth(request: ApiRequest, body: UserCreate):
    """
    Request an authentication code (OTP).

    This endpoint sends an SMS containing a one-time password (OTP)
    to the user's registered phone number for authentication purposes.
    The phone number is normalized before sending the OTP.
    """
    phone = body.phone_normalize()
    if not phone:
        raise BadRequest("Invalid phone number")
    code = await auth_service.send_otp(phone, request.business_code)
    return SuccessResponse(message="OTP sent successfully.")


@auth.post("/confirm")
@openapi.definition(
    body={
        "application/json": UserCodeConfirm.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    description="Confirm OTP code and get tokens",
    summary="Complete authorization flow",
    response=[
        Response(
            {
                "application/json": TokenPair.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            },
            status=HTTPStatus.OK,
        )
    ],
)
@validate(UserCodeConfirm)
@rules(otp_context_required)
async def confirm_auth(request: ApiRequest, body: UserCodeConfirm):
    """
    Confirm the OTP and issue JWT tokens.

    This endpoint verifies the provided OTP against the stored code.
    If the OTP is valid, it marks the code as used, retrieves or
    creates the user associated with the OTP, and issues JSON Web
    Tokens (JWT) for access and refresh.
    """
    otp_context = request.ctx.otp
    if otp_context.code == body.otp:
        await otp_service.set_code_used(otp_context)
        user = await user_service.get_or_create(otp_context.destination)
        access, refresh = await tokens_service.with_context(
            {"request": request}
        ).create_tokens_for_user(user, realm=body.realm, business=body.business)

        return json(serialize_token_pair(access, refresh))

    raise BadRequest("Wrong OTP code")
