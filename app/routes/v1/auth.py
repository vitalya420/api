"""
This module contains the routes for the authentication endpoints.

It provides endpoints to:
- Request an authentication code (OTP) via SMS.
- Confirm the OTP and issue JWT access and refresh tokens.

Endpoints:
- POST /auth/            : Send an SMS with an OTP for authentication.
- POST /auth/confirm     : Verify the OTP and issue tokens upon successful verification.
"""

from sanic import Blueprint, Request, json, BadRequest
from sanic_ext import validate

from app.schemas import UserCreate
from app.schemas.user import UserCodeConfirm
from app.serializers import serialize_token_pair
from app.services import auth_service
from app.services import otp_service
from app.services import tokens_service
from app.services import user_service
from app.security import (rules,
                          otp_context_required,
                          business_id_required)

auth = Blueprint('auth', url_prefix='/auth')


@auth.post('/')
@rules(business_id_required)
@validate(UserCreate)
async def request_auth(request: Request, body: UserCreate):
    """
    Request an authentication code (OTP).

    This endpoint sends an SMS containing a one-time password (OTP)
    to the user's registered phone number for authentication purposes.
    The phone number is normalized before sending the OTP.

    Args:
        request (Request): The Sanic request object containing the
                           request data.
        body (UserCreate): The request body containing user information,
                           including the phone number.

    Returns:
        json: A JSON response indicating the success of the OTP request.

    Raises:
        Exception: Any exceptions raised during the OTP sending process
                   will propagate to the caller.
    """
    await auth_service.send_otp(body.phone_normalize())
    return json({"ok": True})


@auth.post('/confirm')
@validate(UserCodeConfirm)
@rules(otp_context_required, business_id_required)
async def confirm_auth(request: Request, body: UserCodeConfirm):
    """
    Confirm the OTP and issue JWT tokens.

    This endpoint verifies the provided OTP against the stored code.
    If the OTP is valid, it marks the code as used, retrieves or
    creates the user associated with the OTP, and issues JSON Web
    Tokens (JWT) for access and refresh.

    Args:
        request (Request): The Sanic request object containing the
                           request data, including the OTP for verification.
        body (UserCodeConfirm): The request body containing the OTP
                                to be confirmed.

    Returns:
        json: A JSON response indicating success of the confirmation
              and providing the issued access and refresh tokens.

    Raises:
        BadRequest: If the provided OTP does not match the stored code.
    """
    otp_context = request.ctx.otp
    if otp_context.code == body.otp:
        await otp_service.set_code_used(otp_context)
        user = await user_service.get_or_create(otp_context.destination)
        access, refresh = await (tokens_service.
                                 with_context({'request': request})
                                 .issue_token_pair(user, request.ctx.business))
        return json(serialize_token_pair(access, refresh))
    raise BadRequest("Wrong OTP code")
