from typing import Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.schemas.tokens import TokenPair
from app.schemas.user import WebUserResponse


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""


@openapi.component
class OTPSentResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


@openapi.component
class UserAuthorizedResponse(BaseModel):
    user: Optional[WebUserResponse] = None
    tokens: Optional[TokenPair] = None


class AuthResponse(OTPSentResponse, UserAuthorizedResponse):
    pass
