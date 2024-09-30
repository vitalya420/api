from app.db import async_session_factory as _session_factory
from app.services import services as _services_registry

from .service import ServiceFactory
from .fetcher import fetcher

lazy_services = ServiceFactory(_session_factory, _services_registry)
