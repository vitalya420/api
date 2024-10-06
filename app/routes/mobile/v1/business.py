from sanic import Blueprint, json
from sanic_ext.extensions.openapi import openapi

from app import ApiRequest

business = Blueprint("mobile-business", url_prefix="/business")


@business.get("/")
@openapi.definition(
    description="Get information about business in which user is logged in",
    secured={"token": []},
)
async def get_business(request: ApiRequest):
    return json(
        {
            "ok": True,
            "message": "This route returns information about business in which user is logged in",
        }
    )


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
