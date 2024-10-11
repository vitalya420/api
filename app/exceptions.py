from sanic import ServiceUnavailable, BadRequest, NotFound


class EndpointDoNothing(BadRequest):
    message = "This endpoint cannot be accessed."


class BusinessIDRequired(BadRequest):
    message = "The business ID is required."


class InvalidPhoneNumber(BadRequest):
    message = "The phone number is invalid."


class SMSCooldown(ServiceUnavailable):
    message = "SmsCooldown has been exceeded."


class UserExists(Exception):
    pass


class UserDoesNotExist(BadRequest):
    pass


class WrongPassword(BadRequest):
    pass


class UserHasNoBusinesses(BadRequest):
    pass


class BusinessDoesNotExist(NotFound):
    pass


class UnableToCreateBusiness(BadRequest):
    pass


class BusinessCodeNotProvided(BadRequest):
    pass


class RefreshTokenNotFound(BadRequest):
    pass


class YouAreRetardedError(BadRequest):
    pass
