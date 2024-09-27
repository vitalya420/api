from sanic import Request

from app import app


@app.middleware('request', priority=1)
async def security_middleware(request: Request):
    business = request.headers.get('X-Business-Id', None)
    request.ctx.business = business
