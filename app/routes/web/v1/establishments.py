from PIL import UnidentifiedImageError
from sanic import Blueprint, BadRequest, NotFound
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app.decorators import login_required, pydantic_response, rules
from app.request import ApiRequest
from app.schemas import (
    EstablishmentsResponse,
    EstablishmentCreate,
    EstablishmentResponse,
    EstablishmentUpdate,
    FileUploadRequest,
    SuccessResponse,
)
from app.services import business_service
from app.utils.files_helper import save_image_from_request

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
        user.business,
        body.address,
        long=body.longitude,
        lat=body.latitude,
    )
    return EstablishmentResponse.model_validate(created)


@establishments.patch("/<est_id>")
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
@validate(EstablishmentUpdate)
async def update_establishment(
    request: ApiRequest, est_id: int, body: EstablishmentUpdate
):
    pass


@establishments.post("/<est_id>/image")
@openapi.definition(
    body={
        "multipart/form-data": FileUploadRequest.model_json_schema(
            ref_template="#/components/schemas/{model}"
        )
    },
    secured={"token": []},
)
@login_required
@pydantic_response
async def update_establishment_image(request: ApiRequest, est_id: int):
    try:
        image_url = await save_image_from_request(request)
        updated = await business_service.update_establishment_image(
            await request.get_user(), est_id, image_url
        )
        if updated is None:
            raise NotFound(f"Establishment with id {est_id} not found")
        return EstablishmentResponse.model_validate(updated)
    except UnidentifiedImageError:
        return BadRequest("This is not an image")
    except KeyError:
        return BadRequest("Where is image?")


@establishments.delete("/<est_id>")
@openapi.definition(
    secured={"token": []},
)
@pydantic_response
async def delete_establishment(request: ApiRequest, est_id: int):
    deleted = await business_service.delete_establishment(
        await request.get_user(), est_id
    )
    if deleted:
        return SuccessResponse(message=f"Establishments '{deleted.id}' deleted")
    raise NotFound(f"Establishment with id {est_id} not found")


@establishments.patch("/<est_id>/schedule")
async def set_work_schedule(request: ApiRequest, est_id: int):
    pass
