from app.models import AccessToken, RefreshToken
from app.utils.tokens import encode_token


def serialize_token_pair(access_token: AccessToken, refresh_token: RefreshToken) -> dict:
    return {
        "access_token": encode_token(access_token),
        "refresh_token": encode_token(refresh_token),
    }
