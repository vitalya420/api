from functools import wraps

from sanic import Request, Unauthorized, BadRequest, Forbidden

from app.request import ApiRequest
from app.exceptions import BusinessIDRequired
from app.schemas.user import UserCodeConfirm
from app.services import otp_service


def business_id_required(f):
    @wraps(f)
    async def decorated(request: ApiRequest, *args, **kwargs):
        if request.business_code is None:
            raise BusinessIDRequired
        return await f(request, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    async def decorated(request: ApiRequest, *args, **kwargs):
        if not await request.get_user():
            raise Unauthorized
        return await f(request, *args, **kwargs)

    return decorated


def admin_access(f):
    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        user = request.ctx.get_user()
        if not user.is_admin:
            raise Forbidden
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
