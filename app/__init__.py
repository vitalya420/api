from sanic import Sanic
from sanic.log import logger

from app.routes import api, gateway
from app.cache.redis import connect
from app import middlewares


from app.config import config
from app.services import BaseService

app = Sanic(__name__)
app.blueprint([api, gateway])

app.middleware(middlewares.inject_user, attach_to='request', priority=2)
app.middleware(middlewares.inject_business, attach_to='request', priority=1)


@app.after_server_start
async def _init_app_context(app_):
    logger.info('Initializing app context')

    redis_ = await connect()
    BaseService.set_redis(redis_)

    if await redis_.ping():
        logger.info('Redis connection established')
    else:
        logger.error('Redis connection unavailable')
    app_.ctx.redis = redis_


@app.before_server_stop
async def _close_redis(app_):
    await app_.ctx.redis.close()
