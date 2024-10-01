from functools import wraps

from sanic import Request, Unauthorized, BadRequest

from app.exceptions import BusinessIDRequired
from app.schemas.user import UserCodeConfirm
from app.services import otp


def business_id_required(f):
    @wraps(f)
    def decorated(request: Request, *args, **kwargs):
        if request.ctx.business is None:
            raise BusinessIDRequired
        return f(request, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        if request.token is None:
            raise Unauthorized

        return await f(request, *args, **kwargs)

    return decorated


def otp_context_required(f):
    @wraps(f)
    async def decorated(request: Request, body: UserCodeConfirm, *args, **kwargs):
        otp_code = await otp.get_unexpired_otp(body.phone_normalize())
        if otp_code is None:
            raise BadRequest("OTP code is expired")
        if otp_code.destination != body.phone_normalize():
            raise BadRequest("Bruh, wtf")  # this should never happen
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
