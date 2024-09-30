from sanic import Request, BadRequest, Unauthorized

from app.utils.lazy import fetcher
from app.security import decode_token
from app.services import user
from app.utils.tokens import get_token_from_cache_or_db


async def inject_user(request: Request):
    token = request.token

    if token:
        jwt_payload = decode_token(token)

        jti = jwt_payload['jti']
        type_ = jwt_payload['type']

        if type_ != "access":
            raise BadRequest(f"You trying to authorize with {type_} token")

        token_instance = await get_token_from_cache_or_db(jti, type_, request.app.ctx.redis)

        if token_instance is None:
            raise Unauthorized

        user_id = token_instance.user_id
        request.ctx.services.context.update({'user_id': user_id})
        request.ctx.get_user = fetcher(user.get_by_id, user_id)
