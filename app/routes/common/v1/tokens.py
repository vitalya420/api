import asyncio
from http import HTTPStatus
from textwrap import dedent

import jwt
from sanic import Blueprint, BadRequest
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response, Parameter

from app.decorators import rules, login_required, pydantic_response
from app.request import ApiRequest
from app.schemas import (
    ListIssuedTokenResponse,
    TokenPair,
    PaginationQuery,
    RefreshTokenRequest,
    SuccessResponse,
)
from app.services import tokens_service
from app.utils.tokens import decode_token, encode_token

tokens = Blueprint("tokens", url_prefix="/tokens")


@tokens.get("/")
@openapi.definition(
    description=dedent(
        """
        ## Retrieve List of User's Issued Access Tokens
        
        This endpoint returns a list of access tokens that have been issued to the user.
        
        #### Example response
        
        ```json
        {
          "tokens": [
            {
              "jti": "f85c9095-1649-4931-be8c-f71d56027c93",
              "realm": "web",
              "ip_address": "127.0.0.1",
              "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
          ]
        }
        ```
        """
    ),
    parameter=[
        Parameter("page", int, "query"),
        Parameter("per_page", int, "query"),
    ],
    response=[
        Response(
            {
                "application/json": ListIssuedTokenResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            }
        )
    ],
    secured={"token": []},
)
@rules(login_required)
@validate(query=PaginationQuery)
@pydantic_response
async def list_issued_tokens(request: ApiRequest, query: PaginationQuery):
    user = await request.get_user()

    total_coro = tokens_service.count_access_tokens(
        user, request.realm, request.business_code
    )
    issued_tokens_coro = tokens_service.list_user_issued_tokens(
        user,
        request.realm,
        request.business_code,
        query.limit,
        query.offset,
    )
    total, issued_tokens = await asyncio.gather(total_coro, issued_tokens_coro)
    return ListIssuedTokenResponse(
        page=query.page,
        per_page=query.per_page,
        on_page=len(issued_tokens),
        total=total,
        tokens=issued_tokens,
    )


@tokens.post("/refresh")
@openapi.definition(
    body={
        "application/json": RefreshTokenRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    description=dedent(
        """
        ## Issue new token pair with refresh token
        
        This endpoint allows users to obtain a new pair of tokens (access and refresh) using an existing refresh token. 
        The request will succeed only if the following conditions are met:
        
        - The refresh token has not been used before.
        - The user has not logged out using the associated access token.
        - The access token has not been revoked.

        #### Example request
        
        ```json
        {
          "refresh_token": "<refresh token>"
        }
        ```
        
        #### Example response
        
        ```json
        {
          "access_token": "<access token>",
          "refresh_token": "<refresh token>"
        }
        ```
        """
    ),
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
@pydantic_response
async def refresh_token(request: ApiRequest, body: RefreshTokenRequest):
    try:
        payload = decode_token(body.refresh_token)
        access, refresh = await tokens_service.refresh_tokens(payload["jti"], request)
        return TokenPair(
            access_token=encode_token(access), refresh_token=encode_token(refresh)
        )
    except jwt.exceptions.PyJWTError:
        raise BadRequest("Not a token")


@tokens.post("/logout")
@openapi.definition(
    description=dedent(
        """
        ## Logout
        
        This endpoint revokes the current access token and its associated refresh token, 
        effectively logging the user out. 
        """
    ),
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
    await tokens_service.revoke_access_token(await request.get_access_token())
    return SuccessResponse(
        message="You logged out successfully. Token has been revoked."
    )


@tokens.post("/<jti>/revoke")
@openapi.definition(
    description=dedent(
        """
        ## Revoke an access token by its JTI (JWT ID).

        This endpoint invalidates a specific access token using its JTI (JWT ID), preventing any further use. 
        The associated refresh token is also revoked.
        """
    ),
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
@pydantic_response
async def revoke_token(request: ApiRequest, jti: str):
    revoked = await tokens_service.user_revokes_access_token_by_jti(
        await request.get_user(), jti
    )
    if revoked:
        return SuccessResponse(message="Token has been revoked.")
    raise BadRequest
