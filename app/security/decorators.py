from functools import wraps

from sanic import Request, Unauthorized, BadRequest

from app.exceptions import BusinessIDRequired
from app.schemas.user import UserCodeConfirm


def business_id_required(f):
    @wraps(f)
    def decorated(request: Request, *args, **kwargs):
        if request.ctx.business is None:
            raise BusinessIDRequired
        return f(request, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    def decorated(request: Request, *args, **kwargs):
        if request.token is None:
            raise Unauthorized
        return f(request, *args, **kwargs)

    return decorated


def otp_context_required(f):
    @wraps(f)
    async def decorated(request: Request, body: UserCodeConfirm, *args, **kwargs):
        auth_service = request.app.ctx.services.auth
        otp_code = await auth_service.get_otp(body.phone_normalize())
        print(otp_code)
        if not otp_code:
            raise BadRequest("No need to confirm otp")
        request.ctx.otp = otp_code
        return await f(request, body, *args, **kwargs)

    return decorated


def rules(*decorators):
    def wrapper(func):
        @wraps(func)
        async def decorated(*args, **kwargs):
            nonlocal func
            for decorator in reversed(decorators):
                func = decorator(func)
            return await func(*args, **kwargs)

        return decorated

    return wrapper
