from sanic import Blueprint
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app.decorators import login_required, pydantic_response, rules
from app.request import ApiRequest
from app.routes.mobile.v1 import business
from app.schemas import (
    EstablishmentsResponse,
    EstablishmentCreate,
    EstablishmentResponse,
    EstablishmentUpdate,
)
from app.services import business_service

establishments = Blueprint("web-establishments", url_prefix="/establishments")


@establishments.get("/")
@openapi.definition(
    response={
        "application/json": EstablishmentsResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        ),
    },
    secured={"token": []},
)
@login_required
@pydantic_response
async def get_establishments(request: ApiRequest):
    user = await request.get_user()
    establishments = user.business.establishments
    return EstablishmentsResponse(establishments=establishments)


@establishments.post("/")
@openapi.definition(
    body={
        "application/json": EstablishmentCreate.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    response={
        "application/json": EstablishmentResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    secured={"token": []},
)
@login_required
@validate(EstablishmentCreate)
@pydantic_response
async def create_establishment(request: ApiRequest, body: EstablishmentCreate):
    user = await request.get_user()
    created = await business_service.create_establishment(
        user.business, body.address, long=body.longitude, lat=body.latitude, image=body.image
    )
    return EstablishmentResponse.model_validate(created)


@establishments.patch("/<establishment_id>")
@openapi.definition(
    body={
        "application/json": EstablishmentUpdate.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    response={
        "application/json": EstablishmentResponse.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    secured={"token": []},
)
@rules(login_required)
async def update_establishment(request: ApiRequest, establishment_id: int):
    pass


@establishments.delete("/<establishment_id>")
async def delete_establishment(request: ApiRequest, establishment_id: int):
    pass
