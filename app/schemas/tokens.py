from typing import TYPE_CHECKING, Self, Optional

from pydantic import BaseModel, field_validator

from app.enums import Realm
from app.schemas.pagination import PaginatedResponse
from app.utils import encode_token

if TYPE_CHECKING:
    from app.models import AccessToken, RefreshToken


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

    @classmethod
    def from_models(cls, access: "AccessToken", refresh: "RefreshToken") -> Self:
        return cls(
            access_token=encode_token(access), refresh_token=encode_token(refresh)
        )


class IssuedTokenResponse(BaseModel):
    jti: str
    realm: Realm
    ip_address: str
    user_agent: str
    business_code: Optional[str] = None
    issued_at: str
    revoked: bool

    class Config:
        from_attributes = True

    @field_validator("issued_at", mode="before")  # noqa
    @classmethod
    def format_issued_at(cls, value):
        return value.isoformat()


class ListIssuedTokenResponse(PaginatedResponse):
    tokens: list[IssuedTokenResponse]

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str
