from sanic_ext.extensions.openapi import openapi

from .auth import (
    AuthRequest,
    AuthOTPSentResponse,
    AuthWebUserResponse,
    AuthResponse,
    AuthOTPConfirmRequest,
)
from .business import (
    BusinessCreate,
    BusinessResponse,
    ListBusinessClientResponse,
    BusinessUpdate,
)
from .client import ClientUpdateRequest, ClientResponse, AuthorizedClientResponse
from .pagination import (
    PaginationQuery,
    PaginatedResponse,
    BusinessClientPaginatedRequest,
)
from .establishment import (
    EstablishmentCreate,
    EstablishmentUpdate,
    EstablishmentAddress,
    EstablishmentResponse,
    EstablishmentsResponse,
)
from .tokens import (
    TokenPair,
    IssuedTokenResponse,
    ListIssuedTokenResponse,
    RefreshTokenRequest,
)
from .user import UserResponse, WebUserResponse
from .base import SuccessResponse
from .file import FileUploadRequest
from .work_schedule import (
    WorkScheduleCreate,
    WorkScheduleUpdate,
    WorkScheduleCopy,
    WorkScheduleDay,
)

__all__ = [
    "AuthRequest",
    "AuthOTPSentResponse",
    "AuthWebUserResponse",
    "AuthResponse",
    "AuthOTPConfirmRequest",
    "BusinessCreate",
    "BusinessResponse",
    "ListBusinessClientResponse",
    "BusinessUpdate",
    "ClientUpdateRequest",
    "ClientResponse",
    "AuthorizedClientResponse",
    "PaginationQuery",
    "PaginatedResponse",
    "BusinessClientPaginatedRequest",
    "EstablishmentCreate",
    "EstablishmentUpdate",
    "EstablishmentAddress",
    "EstablishmentResponse",
    "EstablishmentsResponse",
    "TokenPair",
    "IssuedTokenResponse",
    "ListIssuedTokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "WebUserResponse",
    "SuccessResponse",
    "FileUploadRequest",
    "WorkScheduleCreate",
    "WorkScheduleUpdate",
    "WorkScheduleCopy",
    "WorkScheduleDay",
]


for model in __all__:
    locals_ = locals()
    openapi.component(locals_[model])
