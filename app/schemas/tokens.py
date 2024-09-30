from typing import List, Optional

from pydantic import BaseModel


class Token(BaseModel):
    jti: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class TokensListPaginated(BaseModel):
    page: int
    per_page: int
    tokens: List[Token] = []


class RefreshTokenRequest(BaseModel):
    refresh_token: str
