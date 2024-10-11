from typing import Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.enums import Realm
from app.schemas.common import HasPhone
from app.schemas.tokens import TokenPair
from app.schemas.user import WebUserResponse


@openapi.component
class AuthRequest(BaseModel):
    phone: str
    realm: Realm
    password: Optional[str] = None
    business: Optional[str] = None


@openapi.component
class AuthConfirmRequest(BaseModel, HasPhone):
    phone: str
    otp: str
    business: str


@openapi.component
class OTPSentResponse(BaseModel):
    success: bool = True
    message: Optional[str] = "OTP Sent successfully"

    class Config:
        from_attributes = True


@openapi.component
class UserAuthorizedResponse(BaseModel):
    user: Optional[WebUserResponse] = None
    tokens: Optional[TokenPair] = None

    class Config:
        from_attributes = True


class AuthResponse(OTPSentResponse, UserAuthorizedResponse):
    class Config:
        from_attributes = True
