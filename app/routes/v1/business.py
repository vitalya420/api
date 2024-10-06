from sanic import Blueprint, json
from sanic_ext import validate, serializer
from sanic_ext.extensions.openapi import openapi

from app import ApiRequest
from app.schemas.business import BusinessCreate, BusinessResponse
from app.security import rules, login_required
from app.security.decorators import admin_access
from app.serializers import serialize_pydantic
from app.services import business_service

business = Blueprint("business", url_prefix="/business")


@business.get("/<business_id:int>")
@openapi.definition(
    secured={"token": []},
    response=[
        {
            "application/json": BusinessResponse.model_json_schema(
                ref_template="#/components/schemas/{model}"
            )
        }
    ],
)
@rules(login_required)
@serializer(serialize_pydantic)
async def get_business(request: ApiRequest, business_id: int):
    instance = await business_service.get_business(business_id)
    return BusinessResponse.model_validate(instance)


@business.patch("/<business_id>")
async def update_business(request: ApiRequest):
    pass
