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
from .tokens import (
    TokenPair,
    IssuedTokenResponse,
    ListIssuedTokenResponse,
    RefreshTokenRequest,
)
from .user import UserResponse, WebUserResponse
from .base import SuccessResponse
from .file import FileUploadRequest

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
    "TokenPair",
    "IssuedTokenResponse",
    "ListIssuedTokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "WebUserResponse",
    "SuccessResponse",
    "FileUploadRequest",
]


for model in __all__:
    locals_ = locals()
    openapi.component(locals_[model])
