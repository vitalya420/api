from http import HTTPStatus

from sanic.exceptions import SanicException


class EndpointDoNothing(SanicException):
    message = "This endpoint cannot be accessed."
    status_code = HTTPStatus.GONE
    quiet = True


class BusinessIDRequired(SanicException):
    message = "The business ID is required."
    status_code = HTTPStatus.BAD_REQUEST
    quiet = True


class InvalidPhoneNumber(SanicException):
    message = "The phone number is invalid."
    status_code = HTTPStatus.BAD_REQUEST
    quiet = True
