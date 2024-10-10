from sanic import Blueprint, json
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app.request import ApiRequest
from app.schemas.business import BusinessCreate, BusinessesResponse, BusinessResponse
from app.security import rules
from app.security.decorators import admin_access
from app.serializers.businesses import serialize_user_businesses
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
async def get_business(request: ApiRequest):
    businesses = (await request.get_user()).businesses
    return json(serialize_user_businesses(businesses))


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
@rules(admin_access)
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
