from typing import List

from app.models import AccessToken


def serialize_issued_tokens(tokens: List[AccessToken]):
    return [{
        "jti": token.jti,
        "ip_address": token.ip_address,
        "user_agent": token.user_agent,
    } for token in tokens]
