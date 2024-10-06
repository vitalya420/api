from .registry import Registry

from app.services import (tokens_service,
                          user_service,
                          auth_service,
                          otp_service)

services_registry = Registry({
    'tokens': tokens_service,
    'user': user_service,
    'auth': auth_service,
    'otp': otp_service
})
