from textwrap import dedent

from sanic import Blueprint, json
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import rules, login_required, pydantic_response
from app.exceptions import YouAreRetardedError
from app.request import ApiRequest
from app.schemas.business import BusinessClientResponse

client = Blueprint("mobile-client", url_prefix="/user")


@client.get("/")
@openapi.definition(
    description=dedent(
        """
        ## Get information about current user (as business client).
        
        #### Example response
        
        ```json
        {
          "first_name": "User 1",
          "last_name": null,
          "business_code": "FGRYOUAYDNKW",
          "qr_code": "1234567890",
          "bonuses": 100,
          "phone": "+15551234567",
          "is_staff": true
        }
        ```
        """
    ),
    response=[
        Response(
            {
                "application/json": BusinessClientResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            }
        )
    ],
    secured={"token": []},
)
@rules(login_required)
@pydantic_response
async def get_client(request: ApiRequest):
    business_client = await request.get_client()
    if business_client is None:
        # This should not happen
        raise YouAreRetardedError("How are you authorized but you are not a client?")
    return BusinessClientResponse.model_validate(business_client)


@client.patch("/")
@openapi.definition(
    description="Update information about client", secured={"token": []}
)
async def update_client(request: ApiRequest):
    return json({"ok": True, "message": "Update information about client"})


@client.delete("/")
@openapi.definition(description="Delete client", secured={"token": []})
async def delete_client(request: ApiRequest):
    return json({"ok": True, "message": "Delete client"})
