from http import HTTPStatus
from textwrap import dedent

from PIL import UnidentifiedImageError
from sanic import Blueprint, BadRequest, NotFound
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

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
    description=dedent(
        """
        ## List all establishments of business
        """
    ),
    response={
        "application/json": openapi_json_schema(EstablishmentsResponse),
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
    description=dedent(
        """
        ## Create a new establishment
        """
    ),
    body={"application/json": openapi_json_schema(EstablishmentCreate)},
    response=Response(
        {"application/json": openapi_json_schema(EstablishmentResponse)},
        status=HTTPStatus.CREATED,
    ),
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
    return EstablishmentResponse.model_validate(created), HTTPStatus.CREATED


@establishment.patch("/<est_id>")
@openapi.definition(
    description=dedent(
        """
        Update existing establishment
        """
    ),
    body={
        "application/json": openapi_json_schema(EstablishmentUpdate),
    },
    response={
        "application/json": openapi_json_schema(EstablishmentResponse),
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
        "multipart/form-data": openapi_json_schema(FileUploadRequest),
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
    description=dedent(
        """
        ## Delete existing establishment
        """
    ),
    response={
        "application/json": openapi_json_schema(SuccessResponse),
    },
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
    response={"application/json": openapi_json_schema(EstablishmentResponse)},
    secured={"token": []},
)
@login_required
@validate(WorkScheduleCreate)
@pydantic_response
async def set_work_schedule(request: ApiRequest, est_id: int, body: WorkScheduleDay):
    ret = await establishment_service.set_work_schedule(est_id, **body.model_dump())
    return EstablishmentResponse.model_validate(ret)


@establishment.delete("/<est_id>/schedule")
@openapi.definition(
    secured={"token": []},
)
@login_required
@pydantic_response
async def delete_establishment_schedule(request: ApiRequest, est_id: int):
    await establishment_service.user_deletes_schedule(await request.get_user(), est_id)
    return SuccessResponse(message=f"Fuck yeah")
