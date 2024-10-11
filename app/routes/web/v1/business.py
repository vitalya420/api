from textwrap import dedent

from sanic import Blueprint, BadRequest, NotFound, Forbidden
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response, Parameter

from app.decorators import rules, login_required, admin_access, pydantic_response
from app.exceptions import YouAreRetardedError
from app.request import ApiRequest
from app.schemas.business import (
    BusinessCreate,
    BusinessesResponse,
    BusinessResponse,
    BusinessCreationResponse,
    BusinessClientsPaginatedResponse,
)
from app.schemas.pagination import PaginationQuery
from app.services import business_service, user_service

business = Blueprint("web-business", url_prefix="/business")


@business.get("/")
@openapi.definition(
    description=dedent(
        """
        ## List businesses which logged in user is owner
        
        #### Example response
        
        ```json
        {
          "businesses": [
            {
              "code": "HRWKGEHCQUTA",
              "name": "Coffee Shop",
              "picture": "<url to image>",
              "owner_id": 1
            }
          ]
        }
        ```
        """
    ),
    response={
        "application/json": BusinessesResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
    secured={"token": []},
)
@rules(login_required)
@pydantic_response
async def get_business(request: ApiRequest):
    businesses = (await request.get_user()).businesses
    return BusinessesResponse(businesses=businesses)


@business.post("/")
@openapi.definition(
    description=dedent(
        """
        ## Create a new business
        
        Admin user (`user.is_admin == True`) can create new businesses. \
        
        
        One of these arguments required: `owner_id` or `owner_phone`.
        
        #### Example request
        
        ```json
        {
          "name": "Coffe Shop",
          "owner_id": 123
        }
        ```
        
        or
        
        ```json
        {
          "name": "Coffe Shop",
          "owner_phone": "+15551234567"
        }
        ```
        
        #### Example response
        
        ```json
        {
          "success": true,
          "message": "Business Coffe Shop created successfully!",
          "business": {
            "code": "NCFNSCBFYSQU",
            "name": "Coffe Shop",
            "picture": null,
            "owner_id": 123
          }
        }
        ```
        """
    ),
    body={
        "application/json": BusinessCreate.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    response=[
        Response(
            {
                "application/json": BusinessCreationResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            }
        )
    ],
    secured={"token": []},
)
@validate(BusinessCreate)
@rules(login_required, admin_access)
@pydantic_response
async def create_business(request: ApiRequest, body: BusinessCreate):
    if (none := (body.owner_id is None and body.owner_phone is None)) or (
        (body.owner_id and body.owner_phone)
    ):
        raise YouAreRetardedError(
            "Have you read the docs? On of there required: owner_id or owner_phone, not {}".format(
                "none" if none else "both"
            )
        )

    if body.owner_id:
        instance = await business_service.create_business(
            name=body.name, owner=body.owner_id
        )
    elif body.owner_phone:
        user = await user_service.get_user(phone=body.owner_phone, use_cache=False)
        if user is None:
            raise NotFound(f"User with phone {body.owner_phone} not found")
        instance = await business_service.create_business(name=body.name, owner=user)
    else:
        # I added this block to make an IDE sure that instance will be created.
        raise BadRequest("💣 No fucking way this happened")

    return BusinessCreationResponse(
        message=f"Business {instance.name} created successfully!", business=instance
    )


@business.get("/<code>")
@openapi.definition(
    description=dedent(
        """
        ## Get business details by it's code

        #### Example response

        ```json
        {
          "code": "HRWKGEHCQUTA",
          "name": "Coffee Shop",
          "picture": "<url to image>",
          "owner_id": 1
        }
        ```
        """
    ),
    response={
        "application/json": BusinessResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
    secured={"token": []},
)
@rules(login_required)
@pydantic_response
async def get_business_by_code(request: ApiRequest, code: str):
    if (that_business := await business_service.get_business(code)) is None:
        raise BadRequest(f"Business {code} not found")
    if that_business.owner != await request.get_user():
        raise Forbidden("Not your business")
    return BusinessResponse.model_validate(that_business)


@business.get("/<code>/clients")
@openapi.definition(
    description=dedent(
        """
        ## Get business clients

        #### Example response

        """
    ),
    parameter=[Parameter("page", int, "query"), Parameter("per_page", int, "query")],
    response={
        "application/json": BusinessClientsPaginatedResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
    secured={"token": []},
)
@rules(login_required)
@validate(query=PaginationQuery)
@pydantic_response
async def get_business_clients(request: ApiRequest, code: str):
    that_business = await business_service.get_business(code)
    if that_business.owner != await request.get_user():
        raise Forbidden("Not your business")
    clients = await business_service.get_clients(that_business)
