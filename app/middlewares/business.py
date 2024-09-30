from sanic import Request

from app.lazy import fetcher


async def inject_business(request: Request):
    business = request.headers.get('X-Business-Id', None)
    request.ctx.get_business = fetcher(lambda: f"need to fetch business {business} from db")
    request.ctx.business = business
