from functools import wraps
from typing import Callable

from sanic import Unauthorized, BadRequest, Forbidden, json

from app.exceptions import BusinessIDRequired
from app.request import ApiRequest
from app.schemas import AuthOTPConfirmRequest
from app.services import otp_service


def business_id_required(f: Callable) -> Callable:
    """
    Decorator to check if the request contains a business ID.

    This decorator checks if the `business_code` attribute exists in the request object.
    If it is `None`, a `BusinessIDRequired` exception is raised, preventing further
    execution. Otherwise, it proceeds to the wrapped function.

    Args:
        f (Callable): The function to be wrapped.

    Returns:
        Callable: The decorated function that ensures a business ID is present.
    """

    @wraps(f)
    async def decorated(request: ApiRequest, *args, **kwargs):
        if request.business_code is None:
            raise BusinessIDRequired
        return await f(request, *args, **kwargs)

    return decorated


def login_required(f: Callable) -> Callable:
    """
    Decorator to ensure that the request is from an authenticated user.

    This decorator checks if the user is authenticated by calling `get_user()` on
    the request. If no user is found, it raises an `Unauthorized` exception.
    If a user is authenticated, it proceeds to the wrapped function.

    Args:
        f (Callable): The function to be wrapped.

    Returns:
        Callable: The decorated function that requires the user to be logged in.
    """

    @wraps(f)
    async def decorated(request: ApiRequest, *args, **kwargs):
        if not await request.get_user():
            raise Unauthorized
        return await f(request, *args, **kwargs)

    return decorated


def admin_access(f: Callable) -> Callable:
    """
    Decorator to ensure that the authenticated user has admin privileges.

    This decorator checks if the authenticated user has admin access by
    calling `get_user()` and checking the `is_admin` attribute. If the user
    is not an admin, it raises a `Forbidden` exception. If the user has admin
    privileges, it proceeds to the wrapped function.

    Args:
        f (Callable): The function to be wrapped.

    Returns:
        Callable: The decorated function that requires admin access.
    """

    @wraps(f)
    async def decorated(request: ApiRequest, *args, **kwargs):
        user = await request.get_user()
        if not user.is_admin:
            raise Forbidden
        return await f(request, *args, **kwargs)

    return decorated


def otp_context_required(f: Callable) -> Callable:
    """
    Decorator to validate OTP context in the request.

    This decorator ensures that a valid OTP (One-Time Password) exists for the request.
    It checks the OTP associated with the provided phone number and business. If no valid
    OTP is found, or if the OTP has expired, it raises a `BadRequest` exception. If a valid
    OTP exists, it sets the OTP context in the request.

    Args:
        f (Callable): The function to be wrapped.

    Returns:
        Callable: The decorated function that requires valid OTP context.
    """

    @wraps(f)
    async def decorated(
        request: ApiRequest, body: AuthOTPConfirmRequest, *args, **kwargs
    ):
        if not body.phone:
            raise BadRequest("Invalid phone number")
        otp_code = await otp_service.get_unexpired_otp(body.phone, body.business)
        if otp_code is None:
            raise BadRequest("OTP code is expired")
        if otp_code.phone != body.phone:
            raise BadRequest("Bruh, wtf")  # this should never happen
        request.set_otp_context(otp_code)
        return await f(request, body, *args, **kwargs)

    return decorated


def rules(*decorators: Callable) -> Callable:
    """
    Combines multiple decorators into one.

    This function allows you to apply multiple decorators to a single function.
    The decorators are applied in the order they are passed to `rules`.

    Args:
        *decorators (Callable): Any number of decorators to apply.

    Returns:
        Callable: A wrapper function with all decorators applied in reverse order.
    """

    def wrapper(func):
        @wraps(func)
        async def decorated(*args, **kwargs):
            nonlocal func
            for decorator in reversed(decorators):
                func = decorator(func)
            return await func(*args, **kwargs)

        return decorated

    return wrapper


def pydantic_response(func: Callable):
    """
    Decorator to convert the return value of a function to a JSON response using Pydantic.

    This decorator automatically serializes the result of a function into a JSON
    response. It assumes the result of the function is a Pydantic model, and calls
    the model's `model_dump()` method to convert it into a dictionary that can be
    serialized as JSON.

    Args:
        func (Callable): The function to be wrapped.

    Returns:
        Callable: The decorated function that returns a JSON response.
    """

    @wraps(func)
    async def decorator(*args, **kwargs):
        response = await func(*args, **kwargs)
        if isinstance(response, tuple):
            model, status_code = response
            return json(model.model_dump(), status=status_code)
        return json(response.model_dump())

    return decorator
