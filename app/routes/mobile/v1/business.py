from textwrap import dedent

from sanic import Blueprint, json, InternalServerError
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import pydantic_response, login_required
from app.request import ApiRequest
from app.schemas import BusinessMinResponse

business = Blueprint("mobile-business", url_prefix="/business")


@business.get("/")
@openapi.definition(
    description=dedent(
        """
        ## Get information about business in which user is logged in
        
        #### Example response:
        
        ```json
        {
          "code": "FGRYOUAYDNKW",
          "name": "Coffe Shop",
          "picture": null
        }
        ```
        """
    ),
    response=[
        Response(
            {
                "application/json": BusinessMinResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            }
        )
    ],
    secured={"token": []},
)
@pydantic_response
@login_required
async def get_business(request: ApiRequest):
    that_business = await request.get_business()
    if not that_business:
        raise InternalServerError("Something went wrong", quiet=True)
    return BusinessMinResponse.model_validate(that_business)


@business.get("/news")
@openapi.definition(
    description="Get news of business in which user is logged in", secured={"token": []}
)
async def get_news(request: ApiRequest):
    return json(
        {
            "ok": True,
            "message": "This route returns news",
        }
    )


@business.post("/rate")
@openapi.definition(
    description="Rate the business in which user is logged in", secured={"token": []}
)
async def rate_business(request: ApiRequest):
    return json(
        {
            "ok": True,
            "message": "Give rate for business",
        }
    )
