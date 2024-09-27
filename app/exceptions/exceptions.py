from http import HTTPStatus

from sanic.exceptions import SanicException


class EndpointDoNothing(SanicException):
    message = "This endpoint cannot be accessed."
    status_code = HTTPStatus.GONE
    quiet = True
