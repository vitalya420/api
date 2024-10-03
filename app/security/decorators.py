from functools import wraps

from sanic import Request, Unauthorized, BadRequest

from app.exceptions import BusinessIDRequired
from app.schemas.user import UserCodeConfirm
from app.services import otp_service


def business_id_required(f):
    @wraps(f)
    def decorated(request: Request, *args, **kwargs):
        if request.ctx.business is None:
            raise BusinessIDRequired
        # Need to check if authorized user access that business which in headers
        if hasattr(request.ctx, "access_token"):
            token_business_id = request.ctx.access_token.business
            if token_business_id != request.ctx.business:
                raise Unauthorized
        return f(request, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        if not request.token:
            raise Unauthorized
        elif request.ctx.access_token is None:
            raise Unauthorized

        return await f(request, *args, **kwargs)

    return decorated


def otp_context_required(f):
    @wraps(f)
    async def decorated(request: Request, body: UserCodeConfirm, *args, **kwargs):
        if not (phone := body.phone_normalize()):
            raise BadRequest("Invalid phone number")
        otp_code = await otp_service.get_unexpired_otp(phone)
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
