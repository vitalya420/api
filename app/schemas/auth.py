from typing import Optional

from pydantic import BaseModel, field_validator

from app.enums import Realm
from app.schemas.business import BusinessResponse
from app.schemas.base import _HasBusiness
from app.schemas.tokens import TokenPair
from app.schemas.user import WebUserResponse
from app.utils import normalize_phone_number


class AuthRequest(BaseModel, _HasBusiness):
    phone: str
    realm: Realm = Realm.web
    password: Optional[str] = None
    business: Optional[str] = None

    @field_validator("phone")  # noqa
    @classmethod
    def normalize_phone(cls, v):
        return normalize_phone_number(phone=v)


class AuthOTPSentResponse(BaseModel):
    success: bool = True
    message: Optional[str] = "OTP code sent successfully"


class AuthWebUserResponse(WebUserResponse):
    business: BusinessResponse
    tokens: TokenPair

    class Config:
        from_attributes = True


class AuthResponse(AuthOTPSentResponse, AuthWebUserResponse):
    pass


class AuthOTPConfirmRequest(BaseModel, _HasBusiness):
    phone: str
    otp: str
    business: str
