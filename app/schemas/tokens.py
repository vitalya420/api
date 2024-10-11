from typing import List, Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi


@openapi.component
class Token(BaseModel):
    jti: str
    realm: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


@openapi.component
class TokensListPaginated(BaseModel):
    # page: int
    # per_page: int
    tokens: List[Token] = []

    class Config:
        from_attributes = True


@openapi.component
class RefreshTokenRequest(BaseModel):
    refresh_token: str


@openapi.component
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
