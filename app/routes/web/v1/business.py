from sanic import Blueprint, json
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app import ApiRequest
from app.schemas.business import BusinessCreate
from app.security import rules
from app.security.decorators import admin_access
from app.services import business_service

business = Blueprint("web-business", url_prefix="/business")


@business.get("/")
async def get_business(request: ApiRequest):
    return json({"ok": True, "message": "Returns stats about business"})


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
        name=body.name, owner_id=body.owner_id
    )
    if instance:
        return json(
            {"ok": True, "message": f"Business {instance.name} created successfully!"}
        )
