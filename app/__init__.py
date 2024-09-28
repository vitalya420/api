from sanic import Sanic
from sanic.log import logger

from app.routes import api
from app.redis import connect
from app.services import services
from app.db import async_session_factory

from app.lazy import ServiceFactory

from app.config import config

app = Sanic(__name__)
app.blueprint(api)

from app import middlewares


@app.after_server_start
async def _init_app_context(app_):
    logger.info('Initializing app context')
    lazy_services = ServiceFactory(async_session_factory, services)
    app_.ctx.services = lazy_services

    redis_ = await connect()

    if await redis_.ping():
        logger.info('Redis connection established')
    else:
        logger.error('Redis connection unavailable')
    app_.ctx.redis = redis_


@app.before_server_stop
async def _close_redis(app_):
    await app_.ctx.redis.close()
