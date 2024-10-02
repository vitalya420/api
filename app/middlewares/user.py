from sanic import Request, BadRequest

from app.security import decode_token
from app.cache.token import get_token_from_cache_or_db
from app.services import user_service
from app.utils.lazy import fetcher


async def inject_user(request: Request):
    token = request.token

    if token:
        jwt_payload = decode_token(token)

        jti = jwt_payload['jti']
        type_ = jwt_payload['type']
        business = jwt_payload['business']

        if type_ != "access":
            raise BadRequest(f"You trying to authorize with {type_} token")

        token_instance = await get_token_from_cache_or_db(jti, request.app.ctx.redis, type_)
        print(f'INSIDE MIDLLEWARE {token_instance=}')
        if token_instance is None:
            request.ctx.access_token = None
            return

        user_id = token_instance.user_id

        request.ctx.access_token = token_instance
        request.ctx.get_user = fetcher(user_service.get_by_id, user_id)
