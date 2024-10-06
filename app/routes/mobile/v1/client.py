from sanic import Blueprint, json
from sanic_ext.extensions.openapi import openapi

from app import ApiRequest

client = Blueprint("mobile-client", url_prefix="/user")


@client.get("/")
@openapi.definition(
    description="Get information about logged in user", secured={"token": []}
)
async def get_client(request: ApiRequest):
    return json(
        {"ok": True, "message": "This route return information about client for him"}
    )


@client.patch("/")
@openapi.definition(
    description="Update information about client", secured={"token": []}
)
async def update_client(request: ApiRequest):
    return json({"ok": True, "message": "Update information about client"})


@client.delete("/")
@openapi.definition(
    description="Delete client", secured={"token": []}
)
async def delete_client(request: ApiRequest):
    return json({"ok": True, "message": "Delete client"})
