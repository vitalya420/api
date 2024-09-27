from sanic import Sanic

from app.routes import api
from app.services import services
from app.db import async_session_factory

from app.lazy import ServiceFactory

app = Sanic(__name__)
app.blueprint(api)

from app import middlewares


@app.after_server_start
def _init_app_context(app_):
    lazy_services = ServiceFactory(async_session_factory, services)
    app_.ctx.services = lazy_services
