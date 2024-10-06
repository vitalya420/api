from typing import Any, Optional

from app.db import async_session_factory as _session_factory


from .service import ServiceFactory
from .fetcher import fetcher
from app.utils.misc import services_registry


def create_lazy_services_factory(context: Optional[dict[Any, Any]] = None) -> ServiceFactory:
    return ServiceFactory(_session_factory, services_registry, context)
