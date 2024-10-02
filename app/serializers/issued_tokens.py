from typing import List

from app.models import AccessToken

from app.schemas.tokens import TokensListPaginated, Token


def serialize_issued_tokens(tokens: List[AccessToken]):
    _tokens = [Token(jti=token.jti, ip_address=token.ip_address, user_agent=token.user_agent) for token in tokens]
    return TokensListPaginated(tokens=_tokens).model_dump()
