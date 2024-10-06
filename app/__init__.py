import os.path
from textwrap import dedent

from sanic import Sanic
from sanic.log import logger

from app.redis import connect
from app.config import config
from app.request import ApiRequest
from app.routes import api
from app.services import BaseService

app = Sanic(__name__, request_class=ApiRequest)
app.extend(
    config={
        "swagger_ui_configuration": {
            "apisSorter": "alpha",
            "operationsSorter": "alpha",
            "docExpansion": "list",
        }
    }
)
app.blueprint([api])

description_md = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "docs/description.md"
)
with open(description_md, encoding="utf-8") as f:
    description = f.read()

app.ext.openapi.describe(
    "API",
    version="1.0.0",
    description=dedent(description),
)

app.ext.openapi.add_security_scheme(
    "token",
    "http",
    scheme="Bearer",
    bearer_format="JWT",
)


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
