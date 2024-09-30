from typing import Any, Optional

from app.db import async_session_factory as _session_factory
from app.services import services as _services_registry

from .service import ServiceFactory
from .fetcher import fetcher


def create_lazy_services_factory(context: Optional[dict[Any, Any]] = None) -> ServiceFactory:
    return ServiceFactory(_session_factory, _services_registry, context)


services = create_lazy_services_factory()
