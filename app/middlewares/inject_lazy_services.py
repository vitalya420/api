from sanic import Request
from app.lazy import create_lazy_services_factory


async def inject_lazy_services(request: Request):
    context = {
        "request": request,
        "ip_address": request.headers.get("X-Real-IP", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
    }

    request.ctx.services = create_lazy_services_factory(context)
