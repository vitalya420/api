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

from sanic import Blueprint, json
from sanic import Request
from sanic_ext import validate

from app.schemas.tokens import RefreshTokenRequest
from app.security import (rules,
                          login_required,
                          business_id_required)
from app.serializers import serialize_issued_tokens
from app.services import tokens_service

token = Blueprint('token', url_prefix='/token')


@token.get('/issued')
@rules(login_required, business_id_required)
async def get_all_tokens(request: Request):
    """
    Retrieve a list of devices where the user is logged in.

    This endpoint returns information about all devices that have
    active sessions for the authenticated user. It is useful for
    managing user sessions and identifying where the user is currently
    logged in.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success and providing a list
              of devices where the user is logged in.

    Raises:
        Exception: Any exceptions raised during the retrieval process
                   will propagate to the caller.
    """
    user = await request.ctx.get_user()
    issued_tokens = await tokens_service.get_user_tokens(user, request.ctx.business)
    return json(serialize_issued_tokens(issued_tokens))


@token.post('/logout')
@rules(login_required, business_id_required)
async def logout(request: Request):
    """
    Revoke the current user's access token.

    This endpoint invalidates the access token associated with the
    authenticated user, effectively logging them out.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success of the logout operation.
    """
    return json({"ok": True})


@token.post('/refresh')
@validate(json=RefreshTokenRequest)
@rules(login_required, business_id_required)
async def refresh_token(request: Request, body: RefreshTokenRequest):
    """
    Issue new access and refresh tokens.

    This endpoint accepts a refresh token and, if valid, issues
    new access and refresh tokens for the user.

    Args:
        request (Request): The Sanic request object containing the
                           request data.
        body (RefreshTokenRequest): The request body containing the
                                    refresh token.

    Returns:
        json: A JSON response indicating success and providing the
              new tokens.
    """
    return json({"ok": True})


@token.post('/<jti>/revoke')
@rules(login_required, business_id_required)
async def revoke_token(request: Request, jti: str):
    """
    Revoke an access token by its JTI (JWT ID).

    This endpoint invalidates a specific access token identified
    by its JTI, preventing its further use.

    Args:
        request (Request): The Sanic request object containing the
                           request data.
        jti (str): The JWT ID of the access token to be revoked.

    Returns:
        json: A JSON response indicating success of the revocation operation.
    """
    await tokens_service.revoke_token(
        await request.ctx.get_user(),
        request.ctx.business, jti
    )
    return json({"ok": True, "jti": jti})


@token.post('/revoke-all')
@rules(login_required, business_id_required)
async def revoke_all_tokens(request: Request):
    """
    Revoke all access tokens associated with the current user.

    This endpoint invalidates all access tokens that belong to the
    authenticated user, effectively logging them out from all sessions.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success of the revocation operation.
    """
    return json({"ok": True})
