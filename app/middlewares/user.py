from sanic import Request

from app.lazy import fetcher, lazy_services
from app.security import decode_token


async def inject_user(request: Request):
    token = request.token
    user_id = decode_token(token).get('user_id')

    request.ctx.get_user = fetcher(lazy_services.user.get_by_id,
                                   user_id)
