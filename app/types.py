from typing import Type, Literal, Union

from app.models import RefreshToken, AccessToken, User, Business

TokenType = Union[
    str,
    Literal["access", "refresh"],
    Type[AccessToken],
    Type[RefreshToken]
]

UserType = Union[
    int,  # user's id
    User,  # user instance
]

BusinessType = Union[
    str, Business
]


def get_token_class(token: TokenType) -> Union[Type[AccessToken], Type[RefreshToken]]:
    if isinstance(token, str) and token in ["access", "refresh"]:
        return AccessToken if token == "access" else RefreshToken
    if token is AccessToken:
        return AccessToken
    if token is RefreshToken:
        return RefreshToken
    raise TypeError("What is this shit")
