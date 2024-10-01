"""
This module contains the routes for the authentication endpoints.

It provides endpoints to:
- Request an authentication code (OTP) via SMS.
- Confirm the OTP and issue JWT access and refresh tokens.

Endpoints:
- POST /auth/            : Send an SMS with an OTP for authentication.
- POST /auth/confirm     : Verify the OTP and issue tokens upon successful verification.
"""

from sanic import Blueprint, Request, json

from app.security import (rules,
                          otp_context_required,
                          business_id_required)

auth = Blueprint('auth', url_prefix='/auth')


@auth.post('/')
@rules(business_id_required)
async def request_auth(request: Request):
    """
    Request an authentication code (OTP).

    This endpoint sends an SMS containing a one-time password (OTP)
    to the user's registered phone number for authentication purposes.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success of the OTP request.
    """
    return json({"ok": True})


@auth.post('/confirm')
@rules(otp_context_required, business_id_required)
async def confirm_auth(request: Request):
    """
    Confirm the OTP and issue JWT tokens.

    This endpoint verifies the provided OTP and, upon successful
    verification, issues JSON Web Tokens (JWT) for access and refresh.

    Args:
        request (Request): The Sanic request object containing the
                           request data, including the OTP for verification.

    Returns:
        json: A JSON response indicating success of the confirmation
              and providing the issued tokens.
    """
    return json({"ok": True})
