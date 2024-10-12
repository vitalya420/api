from datetime import datetime
from typing import Optional, TYPE_CHECKING, Self

from pydantic import BaseModel, field_validator

from app.enums import Realm
from app.utils import encode_token, normalize_phone_number

if TYPE_CHECKING:
    from app.models import AccessToken, RefreshToken


class _HasBusiness:
    business: str

    @property
    def business_code(self):
        return self.business


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

    @classmethod
    def from_models(cls, access: "AccessToken", refresh: "RefreshToken") -> Self:
        return cls(
            access_token=encode_token(access), refresh_token=encode_token(refresh)
        )


class BusinessBase(BaseModel):
    name: str
    code: str
    owner_id: int


class BusinessResponse(BusinessBase):
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    phone: str


class ClientBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    image: Optional[str] = None
    bonuses: float
    qr_code: str
    phone: str
    is_staff: bool

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True


class AuthRequest(BaseModel, _HasBusiness):
    phone: str
    realm: Realm = Realm.web
    password: Optional[str] = None
    business: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v):
        return normalize_phone_number(phone=v)


class AuthOTPSentResponse(BaseModel):
    success: bool = True
    message: Optional[str] = "OTP code sent successfully"


class AuthWebUserResponse(BaseModel):
    user: UserResponse
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


class AuthorizedClientResponse(BaseModel):
    client: ClientResponse
    tokens: TokenPair

    class Config:
        from_attributes = True


class IssuedTokenResponse(BaseModel):
    jti: str
    realm: Realm
    ip_address: str
    user_agent: str
    business_code: str
    issued_at: str

    class Config:
        from_attributes = True

    @field_validator("issued_at", mode="before")  # noqa
    @classmethod
    def format_issued_at(cls, value):
        return value.isoformat()


class ListIssuedTokenResponse(BaseModel):
    page: int
    per_page: int
    on_page: int
    total: int
    tokens: list[IssuedTokenResponse]

    class Config:
        from_attributes = True
