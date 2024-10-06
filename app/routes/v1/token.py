"""
This module provides endpoints for revoking and refreshing tokens.

It includes endpoints to:
- Revoke the current user's access token.
- Issue new access and refresh tokens.
- Revoke a specific access token by its identifier (JTI).
- Revoke all access tokens associated with the current user.

Endpoints:
- POST /token/logout          : Revoke the current user's token.
- POST /token/refresh         : Issue new access and refresh tokens.
- POST /token/<jti>/revoke    : Revoke a specific access token by its JTI.
- POST /token/revoke-all      : Revoke all access tokens associated with the current user.
"""

from http import HTTPStatus

import jwt.exceptions
from sanic import Blueprint, json, BadRequest
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app import ApiRequest
from app.schemas import SuccessResponse
from app.schemas.tokens import RefreshTokenRequest, TokensListPaginated, TokenPair
from app.security import rules, login_required, business_id_required
from app.serializers import serialize_issued_tokens, serialize_token_pair
from app.services import tokens_service
from app.utils.tokens import decode_token

token = Blueprint("token", url_prefix="/token")


@token.get("/issued")
@openapi.definition(
    summary="List all issued access tokens",
    description="List all issued access tokens.",
    response=[
        Response(
            {
                "application/json": TokensListPaginated.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            },
            status=HTTPStatus.OK,
        )
    ],
    secured={"token": []},
)
@rules(login_required, business_id_required)
async def get_all_tokens(request: ApiRequest):
    """
    Retrieve a list of devices where the user is logged in.

    This endpoint returns information about all devices that have
    active sessions for the authenticated user. It is useful for
    managing user sessions and identifying where the user is currently
    logged in.
    """
    user = await request.get_user()
    issued_tokens = await tokens_service.list_user_issued_tokens_tokens(
        user, request.business_code
    )
    return json(serialize_issued_tokens(issued_tokens))


@token.post("/logout")
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


@token.post("/refresh")
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
    """
    Issue new access and refresh tokens.

    This endpoint accepts a refresh token and, if valid, issues
    new access and refresh tokens for the user.
    """
    try:
        payload = decode_token(body.refresh_token)
        issued = await tokens_service.with_context({"request": request}).refresh_tokens(
            payload["jti"]
        )

        return json(serialize_token_pair(*issued))
    except jwt.exceptions.PyJWTError:
        raise BadRequest("Not a token")


@token.post("/<jti>/revoke")
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
@rules(login_required, business_id_required)
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


@token.post("/revoke-all")
@openapi.definition(
    summary="Revoke all",
    description="Revoke all tokens except current one",
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
@rules(login_required, business_id_required)
async def revoke_all_tokens(request: ApiRequest):
    """
    Revoke all access tokens associated with the current user.

    This endpoint invalidates all access tokens that belong to the
    authenticated user, effectively logging them out from all sessions.
    """

    amount = await tokens_service.revoke_all(
        await request.get_user(),
        request.business_code,
        exclude=[(await request.get_access_token()).jti],
    )
    return json({"ok": True, "tokens_revoked": amount})
