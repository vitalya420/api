from sanic import Sanic
from sanic.log import logger

from app.request import ApiRequest
from app.routes import api
from app.redis import connect
from app.base import BaseService


def create_app():
    app = Sanic("LoyaltyProgramAPI", request_class=ApiRequest)
    app.blueprint(api)

    app.extend(
        config={
            "swagger_ui_configuration": {
                "apisSorter": "alpha",
                "operationsSorter": "alpha",
                "docExpansion": "list",
            }
        }
    )

    app.ext.openapi.describe("API", version="1.0.0")

    app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="Bearer",
        bearer_format="JWT",
    )

    @app.middleware("response")
    async def cors(req, res):
        res.headers["Access-Control-Allow-Origin"] = "*"

    @app.after_server_start
    async def _init_app_context(app_):
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
        await app_.ctx.redis.aclose()

    return app
