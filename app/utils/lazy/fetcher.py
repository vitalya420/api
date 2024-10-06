import inspect
from typing import Any, Callable, Coroutine, TypeVar

R = TypeVar("R")


def fetcher(
    func, *func_args: Any, **func_kwargs: Any
) -> Callable[[], Coroutine[Any, Any, R]]:
    """
    Lazily fetch the result of a function call (synchronous or asynchronous) and return it.

    This function is designed to be used in asynchronous contexts where you want to
    delay the execution of a function until its result is actually needed. It can be
    particularly useful in middleware or decorators where you want to cache the result
    of a function call for later use.

    Usage Example:

    async def inject_user_middleware(request):
        user_service = request.app.ctx.services.user
        user_id = get_user_from_token(request.token)
        get_user = fetcher(user_service.get_user, user_id)  # Lazy fetch
        request.ctx.get_user = get_user

    async def some_decorator_before_handler(request):
        user = await request.ctx.get_user()  # Fetches user when needed
        if not user.admin:
            raise Forbidden('Access denied')

    async def handler(request):
        user = await request.ctx.get_user()  # Returns cached user
        return text(f"Hello, {user.name}!")

    :param func: The function or coroutine to be called lazily. It should be a callable
                 that can accept the provided arguments.
    :param func_args: Positional arguments to pass to the function when it is called.
    :param func_kwargs: Keyword arguments to pass to the function when it is called.
    :return: A callable that, when awaited, will execute the function and return its result.
    """

    retval: Any = None
    function_called: bool = False
    is_coroutine_function: bool = inspect.iscoroutinefunction(func)
    is_awaitable: bool = inspect.isawaitable(func)

    def _sync_fetcher() -> Any:
        nonlocal retval, function_called
        if not function_called:
            retval = func(*func_args, **func_kwargs)
            function_called = True
        return retval

    async def _await_function() -> Any:
        nonlocal retval, function_called
        if not function_called:
            retval = await func  # Awaiting the already awaited function
            function_called = True
        return retval

    async def _call_and_await_function() -> R:
        nonlocal retval, function_called
        if not function_called:
            retval = await func(*func_args, **func_kwargs)
            function_called = True
        return retval

    if is_awaitable and not is_coroutine_function:
        return _await_function
    elif is_coroutine_function:
        return _call_and_await_function

    return _sync_fetcher
