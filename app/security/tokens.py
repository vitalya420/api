from datetime import datetime
from typing import Union

import jwt
from sanic import Unauthorized

from app.config import config
from app.models import (AccessToken,
                        RefreshToken)


def encode_token(token: Union[AccessToken, RefreshToken]):
    payload = {
        "jti": token.jti,
        "user_id": token.user_id,
        "business": token.business,
        "issued_at": int(token.issued_at.timestamp()),
        "expires_at": int(token.expires_at.timestamp()),
    }

    if isinstance(token, AccessToken):
        payload["type"] = "access"
    elif isinstance(token, RefreshToken):
        payload["type"] = "refresh"

    return jwt.encode(payload, config['SECRET_KEY'], algorithm="HS256")


def decode_token(token: str, *, raise_exception: bool = True):
    try:
        payload = jwt.decode(token, config['SECRET_KEY'], algorithms=['HS256'])
        now = datetime.utcnow()

        expires_at = payload["expires_at"]
        if expires_at < now.timestamp():
            if raise_exception:
                raise Unauthorized("Provided token is not valid or revoked")

        return payload
    except jwt.exceptions.PyJWTError:
        raise Unauthorized("Provided token is not valid or revoked")
