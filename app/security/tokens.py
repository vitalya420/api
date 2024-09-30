from typing import Union

import jwt

from app.config import config
from app.models import (AccessToken,
                        RefreshToken)


def encode_token(token: Union[AccessToken, RefreshToken]):
    payload = {
        "jti": token.jti,
        "user_id": token.user_id,
        "issued_at": int(token.issued_at.timestamp()),
        "expires_at": int(token.expires_at.timestamp()),
    }

    if isinstance(token, AccessToken):
        payload["type"] = "access"
    elif isinstance(token, RefreshToken):
        payload["type"] = "refresh"

    return jwt.encode(payload, config['SECRET_KEY'], algorithm="HS256")


def decode_token(token: str):
    return dict()
