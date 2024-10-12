from http import HTTPStatus
from textwrap import dedent

from sanic import Blueprint, json
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import rules, login_required, pydantic_response
from app.exceptions import YouAreRetardedError
from app.request import ApiRequest
from app.schemas.business import BusinessClientResponse, BusinessClientUpdateRequest
from app.services import business_service

client = Blueprint("mobile-client", url_prefix="/user")


@client.get("/")
@openapi.definition(
    description=dedent(
        """
        ## Retrieve Information About the Current User (Business Client)
        
        This endpoint provides detailed information about the currently authenticated user
        in the context of a business client. The response includes essential user details
        such as their name, business code, QR code, bonuses, phone number, and staff status.

        #### Example Response
        
        ```json
        {
          "first_name": "User 1",
          "last_name": null,
          "business_code": "FGRYOUAYDNKW",
          "qr_code": "1234567890",
          "bonuses": 100,
          "phone": "+15551234567",
          "is_staff": true
        }
        ```
        """
    ),
    response=[
        Response(
            {
                "application/json": BusinessClientResponse.model_json_schema(
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
async def get_client(request: ApiRequest):
    business_client = await request.get_client()
    if business_client is None:
        # This should not happen
        raise YouAreRetardedError("How are you authorized but you are not a client?")
    return BusinessClientResponse.model_validate(business_client)


@client.patch("/")
@openapi.definition(
    body={
        "application/json": BusinessClientUpdateRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    description=dedent(
        """
        ## Update Information for the Current Client
        
        This endpoint allows the authenticated business client to update their personal information.
        The request body should include the fields that need to be updated. Only the fields provided
        in the request will be modified.

        #### Example Request
        
        ```json
        {
          "first_name": "Ryan",
          "last_name": "Gosling"
        }
        ```
        
        #### Example Response
        
        Upon successful update, the response will return the updated client information:
        
        ```json
        {
          "first_name": "Ryan",
          "last_name": "Gosling",
          "business_code": "FJEQXAACNVCR",
          "qr_code": "2593354118",
          "bonuses": 0,
          "phone": "+15551234567",
          "is_staff": false
        }
        ```
        """
    ),
    response=[
        Response(
            {
                "application/json": BusinessClientResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            },
            status=HTTPStatus.OK,
        )
    ],
    secured={"token": []},
)
@validate(BusinessClientUpdateRequest)
@rules(login_required)
@pydantic_response
async def update_client(request: ApiRequest, body: BusinessClientUpdateRequest):
    updated = await business_service.update_client(
        await request.get_client(), **body.model_dump()
    )
    return BusinessClientResponse.model_validate(updated)


@client.delete("/")
@openapi.definition(description="Delete client", secured={"token": []})
async def delete_client(request: ApiRequest):
    return json({"ok": True, "message": "Delete client"})
