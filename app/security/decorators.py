from functools import wraps

from sanic import Request, Unauthorized

from app.exceptions import BusinessIDRequired


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
