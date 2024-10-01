from sanic import ServiceUnavailable, BadRequest


class EndpointDoNothing(BadRequest):
    message = "This endpoint cannot be accessed."


class BusinessIDRequired(BadRequest):
    message = "The business ID is required."


class InvalidPhoneNumber(BadRequest):
    message = "The phone number is invalid."


class SMSCooldown(ServiceUnavailable):
    message = "SmsCooldown has been exceeded."
