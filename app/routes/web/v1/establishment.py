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
    WorkScheduleCreate,
    WorkScheduleDay,
)
from app.services import establishment_service
from app.utils import openapi_json_schema
from app.utils.files_helper import save_image_from_request

establishment = Blueprint("web-establishments", url_prefix="/establishments")


@establishment.get("/")
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
    establishments = await establishment_service.get_business_establishments(
        user.business
    )
    return EstablishmentsResponse(establishments=establishments)


@establishment.post("/")
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
    created = await establishment_service.create_establishment(
        user.business,
        body.address,
        long=body.longitude,
        lat=body.latitude,
    )
    return EstablishmentResponse.model_validate(created)


@establishment.patch("/<est_id>")
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
@pydantic_response
async def update_establishment(
    request: ApiRequest, est_id: int, body: EstablishmentUpdate
):
    updated = await establishment_service.update_establishment(
        est_id, **body.model_dump()
    )
    return EstablishmentResponse.model_validate(updated)


@establishment.post("/<est_id>/image")
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
        updated = await establishment_service.set_establishment_image(
            est_id, await request.get_user(), image_url
        )
        if updated is None:
            raise NotFound(f"Establishment with id {est_id} not found")
        return EstablishmentResponse.model_validate(updated)
    except UnidentifiedImageError:
        return BadRequest("This is not an image")
    except KeyError:
        return BadRequest("Where is image?")


@establishment.delete("/<est_id>")
@openapi.definition(
    secured={"token": []},
)
@pydantic_response
async def delete_establishment(request: ApiRequest, est_id: int):
    deleted = await establishment_service.delete_establishment(
        await request.get_user(), est_id
    )
    if deleted:
        return SuccessResponse(message=f"Establishments '{deleted.id}' deleted")
    raise NotFound(f"Establishment with id {est_id} not found")


@establishment.patch("/<est_id>/schedule")
@openapi.definition(
    body={"application/json": openapi_json_schema(WorkScheduleCreate)},
    secured={"token": []},
)
@login_required
@validate(WorkScheduleCreate)
@pydantic_response
async def set_work_schedule(request: ApiRequest, est_id: int, body: WorkScheduleDay):
    ret = await establishment_service.set_work_schedule(est_id, **body.model_dump())
    return EstablishmentResponse.model_validate(ret)
