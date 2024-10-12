from http import HTTPStatus
from textwrap import dedent

from sanic import Blueprint, BadRequest, InternalServerError
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import otp_context_required, pydantic_response
from app.enums import Realm
from app.request import ApiRequest
from app.schemas import (
    AuthRequest,
    AuthResponse,
    AuthWebUserResponse,
    TokenPair,
    AuthOTPSentResponse,
    AuthOTPConfirmRequest,
    AuthorizedClientResponse,
)
from app.services import (
    auth_service,
    otp_service,
    user_service,
    tokens_service,
    business_service,
)

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
            "id": 1,
            "is_admin": true
          },
          "business": {
            "name": "Coffee Shop",
            "code": "SHQDZGVTBITNYBBY",
            "owner_id": 1
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
            {
                "application/json": AuthResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            },
            status=HTTPStatus.OK,
            description="Code sent successfully.",
        )
    ],
    summary="Authorize user",
)
@validate(AuthRequest)
@pydantic_response
async def authorization(request: ApiRequest, body: AuthRequest):
    if not body.password and body.realm == Realm.web:
        raise BadRequest("Authorization in WEB requires password.")
    if not body.business and body.realm == Realm.mobile:
        raise BadRequest("Authorization in mobile app requires business code.")

    if body.realm == Realm.web:
        user, access, refresh = await auth_service.with_context(
            {"request": request}
        ).business_admin_login(body.phone, body.password)
        return AuthWebUserResponse(
            user=user,
            business=user.business,
            tokens=TokenPair.from_models(access, refresh),
        )
    elif body.realm == Realm.mobile:
        await auth_service.send_otp(body.phone, body.realm, body.business)
        return AuthOTPSentResponse(message="OTP sent successfully.")
    raise InternalServerError("Unexpected error.", quiet=True)


@auth.post("/confirm")
@openapi.definition(
    body={
        "application/json": AuthOTPConfirmRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    description=dedent(
        """
        ## Complete an authorization
        
        Complete an authorization using sent one time password and get tokens
        
        #### Example request
        
        ```json
        {
          "phone": "+15551234567",
          "otp": "000000",
          "business": "SOMECODE",
        }
        ```
        
        If code is correct you will receive the following response:
        
        ```json
        {
          "client": {
            "business_code": "FGRYOUAYDNKW",
            "qr_code": "1234567890",
            "bonuses": 0
            "phone": "+15551234567"
          },
          "tokens": {
            "access_token": "<access token>",
            "refresh_token": "<refresh token>"
          }
        ```
        """
    ),
    response=Response(
        {
            "application/json": AuthorizedClientResponse.model_json_schema(
                ref_template="#/components/schemas/{model}"
            )
        },
        status=HTTPStatus.OK,
    ),
    summary="Complete an authorization with OTP",
)
@validate(AuthOTPConfirmRequest)
@otp_context_required
@pydantic_response
async def confirm_auth(request: ApiRequest, body: AuthOTPConfirmRequest):
    if request.otp_context.code != body.otp:
        raise BadRequest("Wrong or expired otp code")

    await otp_service.set_code_used(request.otp_context)
    user = await user_service.get_or_create(request.otp_context.phone)
    client = await business_service.get_or_create_client(
        request.otp_context.business_code, user
    )

    access, refresh = await tokens_service.create_tokens(
        user.id,
        request=request,
        realm=request.otp_context.realm,
        business_code=request.otp_context.business_code,
    )
    return AuthorizedClientResponse(
        client=client, tokens=TokenPair.from_models(access, refresh)
    )
