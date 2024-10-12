import datetime
import uuid
from typing import Union

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped

from app.base import BaseCachableModel
from app.const import UUID_LENGTH, BUSINESS_CODE_LENGTH, MAX_STRING_LENGTH
from app.enums import Realm


class _BaseToken(BaseCachableModel):
    """
    An abstract base class representing a token in the system.

    This class provides common attributes and methods for token management, including
    properties for token identification, user association, and expiration handling.

    Attributes:
        jti (str): The unique identifier for the token (primary key), generated as a UUID.
        realm (Realm): The realm or context in which the token is used, represented as an enum.
        user_id (int): The ID of the user associated with the token. This is a foreign key referencing
            the 'users' table and is non-nullable.
        business_code (str): The code of the business associated with the token. This is a foreign key
            referencing the 'businesses' table and can be null if not applicable.
        revoked (bool): A flag indicating whether the token has been revoked. Defaults to False.
        issued_at (datetime): The timestamp indicating when the token was issued. This is a non-nullable datetime.
        expires_at (datetime): The timestamp indicating when the token will expire. This is a non-nullable datetime.

    Methods:
        is_alive() -> bool: Checks if the token is still valid (not expired and not revoked).
    """

    __abstract__ = True
    __cache_key_attr__ = "jti"

    jti: Mapped[str] = Column(
        String(UUID_LENGTH), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    realm: Mapped[Realm] = Column(Enum(Realm), nullable=False)
    user_id: Mapped[int] = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    business_code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    revoked: Mapped[bool] = Column(Boolean, default=False)
    issued_at: Mapped[datetime] = Column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = Column(DateTime, nullable=False)

    def is_alive(self):
        now = datetime.datetime.utcnow()  # noqa
        return self.expires_at > now and not self.revoked


class RefreshToken(_BaseToken):
    """
    Represents a refresh token used to obtain new access tokens.

    Attributes:
        access_token_jti (Union[str, None]): The JTI of the associated access token. This is a foreign key
            referencing the 'access_tokens' table and can be null if not applicable.

    Methods:
        __repr__() -> str: Returns a string representation of the RefreshToken instance, including its JTI,
            realm, user ID, and whether it is alive.
    """

    __tablename__ = "refresh_tokens"
    type_str = "refresh"

    access_token_jti: Mapped[Union[str, None]] = Column(
        String(UUID_LENGTH), ForeignKey("access_tokens.jti"), nullable=True
    )

    def __repr__(self):
        return f"<RefreshToken(jti='{self.jti}', realm={self.realm}, user_id={self.user_id}, alive={self.is_alive()})>"


class AccessToken(_BaseToken):
    """
    Represents an access token used for authenticating requests.

    Attributes:
        ip_address (Union[str, None]): The IP address from which the access token was issued. This can be null.
        user_agent (Union[str, None]): The user agent string from which the access token was issued. This can be null.
        refresh_token_jti (Union[str, None]): The JTI of the associated refresh token. This is a foreign key
            referencing the 'refresh_tokens' table and can be null if not applicable.

    Methods:
        __repr__() -> str: Returns a string representation of the AccessToken instance, including its JTI,
            realm, user ID, and whether it is alive.
    """

    __tablename__ = "access_tokens"
    type_str = "access"

    ip_address: Mapped[Union[str, None]] = Column(
        String(MAX_STRING_LENGTH), nullable=True
    )
    user_agent: Mapped[Union[str, None]] = Column(
        String(MAX_STRING_LENGTH), nullable=True
    )
    refresh_token_jti: Mapped[Union[str, None]] = Column(
        String(UUID_LENGTH), ForeignKey("refresh_tokens.jti"), nullable=True
    )

    def __repr__(self):
        return f"<AccessToken(jti='{self.jti}', realm={self.realm}, user_id={self.user_id}, alive={self.is_alive()})>"
