from app.models import User
from app.schemas.user import WebUserResponse
from app.serializers.token_pair import serialize_token_pair


def serialize_user(user: User) -> dict:
    return {}


def serialize_web_user(user: User, access, refresh) -> dict:
    return {
        "user": WebUserResponse.model_validate(user).model_dump(),
        "tokens": serialize_token_pair(access, refresh),
    }
