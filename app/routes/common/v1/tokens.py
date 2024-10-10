from http import HTTPStatus

import jwt
from sanic import Blueprint, json, BadRequest
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.request import ApiRequest
from app.schemas.response import SuccessResponse
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
        issued = await tokens_service.refresh_tokens(payload["jti"], request)

        return json(serialize_token_pair(*issued))
    except jwt.exceptions.PyJWTError:
        raise BadRequest("Not a token")


@tokens.post("/logout")
@openapi.definition(
    summary="Logout",
    description="Revokes current access token.",
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
    secured={"token": []},
)
@rules(login_required)
async def logout(request: ApiRequest):
    """
    Revoke the current user's access token.

    This endpoint invalidates the access token associated with the
    authenticated user, effectively logging them out.
    """

    await tokens_service.revoke_access_token(await request.get_access_token())

    return json({"ok": True})


@tokens.post("/<jti>/revoke")
@openapi.definition(
    summary="Revoke",
    description="Revoke token by it's jti",
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
    secured={"token": []},
)
@rules(login_required)
async def revoke_token(request: ApiRequest, jti: str):
    """
    Revoke an access token by its JTI (JWT ID).

    This endpoint invalidates a specific access token identified
    by its JTI, preventing its further use.
    """
    revoked = await tokens_service.user_revokes_access_token_by_jti(
        await request.get_user(), jti
    )
    if revoked:
        return json({"ok": True, "jti": jti})
    raise BadRequest
