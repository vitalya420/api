from typing import Type

from sanic import Sanic
from sanic.log import logger

from app.request import ApiRequest
from app.routes import api
from app.redis import connect
from app.base import BaseService
from app.services import tokens_service, user_service, business_service


async def stub():
    pass


def create_request_class() -> Type[ApiRequest]:
    """
    Create and configure the ApiRequest class with necessary getters.

    This function initializes the ApiRequest class and sets up various getter functions
    that allow retrieval of specific values from the database. The purpose of this setup
    is to avoid circular imports in services that require access to the request class.

    The following getters are configured:
        - `token_getter`: A function to retrieve the access token.
        - `user_getter`: A function to retrieve user information.
        - `business_getter`: A function to retrieve business information.
        - `client_getter`: A stub function for client retrieval.

    Returns:
        Type[ApiRequest]: The configured ApiRequest class with the specified getters set.

    Example:
        >>> RequestClass = create_request_class()
        >>> request_instance = RequestClass()
        >>> token = request_instance.get_access_token()
    """
    return ApiRequest.set_getters(
        token_getter=tokens_service.get_access_token,
        user_getter=user_service.get_user,
        business_getter=business_service.get_business,
        client_getter=stub,
    )


def create_app() -> Sanic:
    """
    Create and configure a Sanic application for the Loyalty Program API.

    This function initializes the Sanic application, sets up middleware,
    configures OpenAPI documentation, and establishes a connection to Redis.

    Returns:
        Sanic: The configured Sanic application instance.
    """
    app = Sanic("LoyaltyProgramAPI", request_class=create_request_class())
    app.blueprint(api)

    # Configure Swagger UI settings
    app.extend(
        config={
            "swagger_ui_configuration": {
                "apisSorter": "alpha",
                "operationsSorter": "alpha",
                "docExpansion": "list",
            }
        }
    )

    # Describe the API for OpenAPI documentation
    app.ext.openapi.describe("API", version="1.0.0")

    # Add security scheme for JWT authentication
    app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="Bearer",
        bearer_format="JWT",
    )

    @app.middleware("response")
    async def cors(req, res):
        """
        Middleware to handle CORS by allowing all origins.

        Args:
            req: The incoming request object.
            res: The outgoing response object.
        """
        res.headers["Access-Control-Allow-Origin"] = "*"

    @app.after_server_start
    async def _init_app_context(app_):
        """
        Initialize application context after the server starts.

        This function establishes a connection to Redis and sets it in the
        application context. It also logs the status of the Redis connection.

        Args:
            app_ (Sanic): The Sanic application instance.
        """
        logger.info("Initializing app context")

        redis_ = await connect()
        BaseService.set_redis(redis_)

        if await redis_.ping():
            logger.info("Redis connection established")
        else:
            logger.error("Redis connection unavailable")
        app_.ctx.redis = redis_

    @app.before_server_stop
    async def _close_redis(app_):
        """
        Close the Redis connection before the server stops.

        Args:
            app_ (Sanic): The Sanic application instance.
        """
        await app_.ctx.redis.aclose()

    return app
