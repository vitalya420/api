from textwrap import dedent

from sanic import Blueprint, BadRequest
from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Response

from app.decorators import pydantic_response, login_required
from app.request import ApiRequest
from app.schemas import WebUserResponse, UserResponse

user = Blueprint("web-user", url_prefix="/user")


@user.route("/")
@openapi.definition(
    description=dedent(
        """
        ## Get information about user

        #### Example response:

        ```json
        {
          "phone": "+15551234567",
          "is_admin": false,
        }
        ```
        """
    ),
    response=[
        Response(
            {
                "application/json": WebUserResponse.model_json_schema(
                    ref_template="#/components/schemas/{model}"
                )
            }
        )
    ],
    secured={"token": []},
)
@login_required
@pydantic_response
async def get_user(request: ApiRequest):
    logged_user = await request.get_user()
    if logged_user is None:
        raise BadRequest
    return WebUserResponse(user=UserResponse.model_validate(logged_user))
