from sanic import Request, BadRequest

from app.security import decode_token
from app.services import user_service, tokens_service
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

        token_instance = await tokens_service.get_access_token_with_cache(jti)

        if token_instance is None:
            request.ctx.access_token = None
            return

        user_id = token_instance.user_id

        request.ctx.access_token = token_instance
        request.ctx.get_user = fetcher(user_service.get_user_by_id, user_id)
