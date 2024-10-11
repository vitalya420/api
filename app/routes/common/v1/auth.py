from http import HTTPStatus
from textwrap import dedent

from sanic import Blueprint, json, BadRequest
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.exceptions import (
    WrongPassword,
    UserHasNoBusinesses,
    UserDoesNotExist,
    YouAreRetardedError,
)
from app.request import ApiRequest
from app.schemas import SuccessResponse
from app.schemas.auth import AuthRequest, AuthConfirmRequest
from app.enums import Realm
from app.schemas.response import AuthResponse
from app.security import otp_context_required
from app.serializers import serialize_token_pair
from app.serializers.user import serialize_web_user
from app.services import auth_service, otp_service, user_service, tokens_service

auth = Blueprint("auth", url_prefix="/auth")


@auth.post("/")
@openapi.definition(
    body={
        "application/json": AuthRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    description=dedent(
        """
        ## Start an Authorization Flow

        This endpoint is used for authorization in both mobile and admin web applications.
        
        ### Mobile Application Authorization
        
        To authorize in a mobile application, you need to provide the following:
        
        - **Phone Number**: The user's phone number.
        - **Realm**: Set this to `'mobile'`.
        - **Business Code**: The specific code associated with the business.
        
        #### Example Request
        
        ```json
        {
          "phone": "+15551234567",
          "realm": "mobile",
          "business": "SOMECODE"
        }
        ```
        
        If the request is successful, meaning the business with the provided code exists and the phone number is valid, 
        you will receive the following response:
        
        ```json
        {
          "success": true,
          "message": "OTP sent successfully."
        }
        ```
        
        ### Web Application Authorization
        
        For authorization in a web application, you need to provide:
        - **Owner's Phone Number**: The phone number of the business owner.
        - **Password**: The password associated with the account.
        - **Realm**: Set this to `'web'`.
        
        **Note**: Do not include the business code in this request, as it will be ignored.
        
        #### Example Request
        
        ```json
        {
          "phone": "+15551234567",
          "realm": "web",
          "password": "my-password"
        }
        ```
        
        If the request is successful, meaning the user has businesses to manage and user has password, you will receive the following response:
        
        ```json
        {
          "user": {
            "phone": "+15551234567",
            "businesses": [
              {
                "code": "HRWKGEHCQUTA",
                "name": "My Business Name"
              }
            ]
          },
          "tokens": {
            "access_token": "<access token>",
            "refresh_token": "<refresh token>"
          }
        }
        ```
        """
    ),
    response=[
        Response(
            {"application/json": AuthResponse.model_json_schema(
                ref_template="#/components/schemas/{model}"
            )},
            status=HTTPStatus.OK,
            description="Code sent successfully.",
        )
    ],
)
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
        return json(SuccessResponse(message="OTP sent successfully.").model_dump())

    return json({"ok": True})


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
        raise BadRequest("Wrong otp code.")
    raise BadRequest
