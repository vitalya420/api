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
from sanic import Request
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response, Parameter

from app.cache.token import delete_token_from_cache
from app.schemas import SuccessResponse
from app.schemas.tokens import RefreshTokenRequest, TokensListPaginated, TokenPair
from app.security import (rules,
                          login_required,
                          business_id_required, decode_token)
from app.serializers import serialize_issued_tokens, serialize_token_pair
from app.services import tokens_service

token = Blueprint('token', url_prefix='/token')


@token.get('/issued')
@openapi.definition(
    parameter=Parameter('X-Business-ID', str, "header", "Business ID", required=True),
    summary='List all issued access tokens',
    description='List all issued access tokens.',
    response=[Response({"application/json": TokensListPaginated.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )}, status=HTTPStatus.OK)],
    secured={"token": []},
)
@rules(login_required, business_id_required)
async def get_all_tokens(request: Request):
    """
    Retrieve a list of devices where the user is logged in.

    This endpoint returns information about all devices that have
    active sessions for the authenticated user. It is useful for
    managing user sessions and identifying where the user is currently
    logged in.
    """
    user = await request.ctx.get_user()
    issued_tokens = await tokens_service.get_user_tokens(user, request.ctx.business)
    return json(serialize_issued_tokens(issued_tokens))


@token.post('/logout')
@openapi.definition(
    parameter=Parameter('X-Business-ID', str, "header", "Business ID", required=True),
    summary='Logout',
    description='Revokes current access token.',
    response=[Response({"application/json": SuccessResponse.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )}, status=HTTPStatus.OK)],
    secured={"token": []},
)
@rules(login_required, business_id_required)
async def logout(request: Request):
    """
    Revoke the current user's access token.

    This endpoint invalidates the access token associated with the
    authenticated user, effectively logging them out.
    """

    revoked = await tokens_service.revoke_token(
        await request.ctx.get_user(),
        request.ctx.business,
        request.ctx.access_token.jti
    )
    redis = request.app.ctx.redis
    for revoked_token in revoked:
        type_, jti = revoked_token
        await delete_token_from_cache(jti, redis, type_)
    return json({"ok": True})


@token.post('/refresh')
@openapi.definition(
    body={"application/json": RefreshTokenRequest.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )},
    parameter=Parameter('X-Business-ID', str, "header", "Business ID", required=True),
    summary='Refresh',
    description='Create new token pair with refresh token',
    response=[Response({"application/json": TokenPair.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )}, status=HTTPStatus.OK)]
)
@validate(json=RefreshTokenRequest)
@rules(business_id_required)
async def refresh_token(request: Request, body: RefreshTokenRequest):
    """
    Issue new access and refresh tokens.

    This endpoint accepts a refresh token and, if valid, issues
    new access and refresh tokens for the user.
    """
    try:
        payload = decode_token(body.refresh_token)
        if payload['business'] != request.ctx.business:
            raise BadRequest("Invalid token")
        revoked, issued = await (tokens_service.
                                 with_context({"request": request}).
                                 refresh(payload))

        redis = request.app.ctx.redis
        for revoked_token in revoked:
            type_, jti = revoked_token
            await delete_token_from_cache(jti, redis, type_)

        return json(serialize_token_pair(*issued))
    except jwt.exceptions.PyJWTError:
        raise BadRequest("Not a token")


@token.post('/<jti>/revoke')
@openapi.definition(
    parameter=Parameter('X-Business-ID', str, "header", "Business ID", required=True),
    summary='Revoke',
    description='Revoke token by it\'s jti',
    response=[Response({"application/json": SuccessResponse.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )}, status=HTTPStatus.OK)],
    secured={"token": []},
)
@rules(login_required, business_id_required)
async def revoke_token(request: Request, jti: str):
    """
    Revoke an access token by its JTI (JWT ID).

    This endpoint invalidates a specific access token identified
    by its JTI, preventing its further use.
    """
    revoked = await tokens_service.revoke_token(
        await request.ctx.get_user(),
        request.ctx.business, jti
    )
    redis = request.app.ctx.redis
    for revoked_token in revoked:
        type_, jti = revoked_token
        await delete_token_from_cache(jti, redis, type_)
    return json({"ok": True, "jti": jti})


@token.post('/revoke-all')
@openapi.definition(
    parameter=Parameter('X-Business-ID', str, "header", "Business ID", required=True),
    summary='Revoke all',
    description='Revoke all tokens except current one',
    response=[Response({"application/json": SuccessResponse.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )}, status=HTTPStatus.OK)],
    secured={"token": []},
)
@rules(login_required, business_id_required)
async def revoke_all_tokens(request: Request):
    """
    Revoke all access tokens associated with the current user.

    This endpoint invalidates all access tokens that belong to the
    authenticated user, effectively logging them out from all sessions.
    """

    user_ = await request.ctx.get_user()
    issued_tokens = await tokens_service.get_user_tokens(
        user_, request.ctx.business
    )

    count = 0

    redis = request.app.ctx.redis
    for issued_token in issued_tokens:
        if issued_token != request.ctx.access_token:
            revoked = await tokens_service.revoke_token(
                user_, request.ctx.business, issued_token.jti
            )
            count += 1

            for revoked_token in revoked:
                type_, jti = revoked_token
                await delete_token_from_cache(jti, redis, type_)

    return json({"ok": True, "tokens_revoked": count})
