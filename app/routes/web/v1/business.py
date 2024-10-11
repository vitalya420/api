from sanic import Blueprint, json
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app.decorators import rules, login_required, admin_access, pydantic_response
from app.request import ApiRequest
from app.schemas.business import BusinessCreate, BusinessesResponse, BusinessResponse
from app.services import business_service

business = Blueprint("web-business", url_prefix="/business")


@business.get("/")
@openapi.definition(
    secured={"token": []},
    response={
        "application/json": BusinessesResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
)
@rules(login_required)
@pydantic_response
async def get_business(request: ApiRequest):
    businesses = (await request.get_user()).businesses
    return BusinessesResponse(businesses=businesses)


@business.post("/")
@openapi.definition(
    body={
        "application/json": BusinessCreate.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    secured={"token": []},
)
@validate(BusinessCreate)
@rules(login_required, admin_access)
async def create_business(request: ApiRequest, body: BusinessCreate):
    instance = await business_service.create_business(
        name=body.name, owner=body.owner_id
    )

    return json(
        {
            "ok": True,
            "message": f"Business {instance.name} created successfully!",
            "business": BusinessResponse.model_validate(instance).model_dump(),
        }
    )
