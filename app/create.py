from sanic import Sanic
from sanic.log import logger

from app.request import ApiRequest
from app.routes import api
from app.redis import connect
from app.base import BaseService


def create_app() -> Sanic:
    """
    Create and configure a Sanic application for the Loyalty Program API.

    This function initializes the Sanic application, sets up middleware,
    configures OpenAPI documentation, and establishes a connection to Redis.

    Returns:
        Sanic: The configured Sanic application instance.
    """
    app = Sanic("LoyaltyProgramAPI", request_class=ApiRequest)
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
