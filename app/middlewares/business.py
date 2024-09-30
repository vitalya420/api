from sanic import Request

from app.lazy import fetcher
from app.lazy import lazy_services


async def inject_business_to_ctx(request: Request):
    business = request.headers.get('X-Business-Id', None)
    request.ctx.get_business = fetcher(lambda: f"need to fetch business {business} from db")
    request.ctx.business = business
