from http import HTTPStatus

import jwt
from sanic import Blueprint, json, BadRequest
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app import ApiRequest
from app.schemas.tokens import RefreshTokenRequest, TokenPair
from app.security import rules, login_required
from app.serializers import serialize_issued_tokens, serialize_token_pair
from app.services import tokens_service
from app.utils.tokens import decode_token

tokens = Blueprint("tokens", url_prefix="/tokens")


@tokens.get("/")
@openapi.definition(secured={"token": []})
@rules(login_required)
async def list_issued_tokens(request: ApiRequest):
    issued_tokens = await tokens_service.list_user_issued_tokens(
        await request.get_user(), request.realm, request.business_code
    )
    return json(serialize_issued_tokens(issued_tokens))


@tokens.post("/refresh")
@openapi.definition(
    body={
        "application/json": RefreshTokenRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    summary="Refresh",
    description="Create new token pair with refresh token",
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
@validate(json=RefreshTokenRequest)
async def refresh_token(request: ApiRequest, body: RefreshTokenRequest):
    try:
        payload = decode_token(body.refresh_token)
        issued = await tokens_service.with_context({"request": request}).refresh_tokens(
            payload["jti"]
        )

        return json(serialize_token_pair(*issued))
    except jwt.exceptions.PyJWTError:
        raise BadRequest("Not a token")
