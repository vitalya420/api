from textwrap import dedent

from sanic import Blueprint, BadRequest, NotFound, Forbidden
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response, Parameter

from app.decorators import rules, login_required, admin_access, pydantic_response
from app.exceptions import YouAreRetardedError
from app.request import ApiRequest
from app.schemas import (
    BusinessResponse,
    BusinessCreate,
    ListBusinessClientResponse,
    BusinessClientPaginatedRequest,
    BusinessUpdate,
)
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
        "application/json": BusinessResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
    secured={"token": []},
)
@rules(login_required)
@pydantic_response
async def get_business(request: ApiRequest):
    return BusinessResponse.model_validate((await request.get_user()).business)


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
                "application/json": BusinessResponse.model_json_schema(
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

    return BusinessResponse.model_validate(instance)


@business.patch("/")
@openapi.definition(
    body={"application/json": BusinessUpdate.model_json_schema()},
    secured={"token": []},
)
@login_required
@validate(BusinessUpdate)
@pydantic_response
async def update_business(request: ApiRequest, body: BusinessUpdate):
    bis = (await request.get_user()).business
    updated = await business_service.update_business(bis, **body.model_dump())
    return BusinessResponse.model_validate(updated)


@business.get("/clients")
@openapi.definition(
    description=dedent(
        """
        ## Get business clients

        #### Example response

        """
    ),
    parameter=[
        Parameter("page", int, "query"),
        Parameter("per_page", int, "query"),
        Parameter("staff_only", bool, "query"),
    ],
    response={
        "application/json": BusinessResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
    secured={"token": []},
)
@rules(login_required)
@validate(query=BusinessClientPaginatedRequest)
@pydantic_response
async def get_business_clients(
    request: ApiRequest, query: BusinessClientPaginatedRequest
):
    that_business = (await request.get_user()).business

    clients = await business_service.get_clients(
        that_business, query.staff_only, query.limit, query.offset
    )
    clients_total = await business_service.count_clients(
        that_business, query.staff_only
    )

    return ListBusinessClientResponse(
        page=query.page,
        per_page=query.per_page,
        on_page=len(clients),
        total=clients_total,
        clients=clients,
    )
