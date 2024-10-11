import datetime
import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.config import config
from app.enums import Realm
from app.base import BaseCachableModel


class Token(BaseCachableModel):
    """
    Abstract base class for tokens.

    This class serves as a base for different types of tokens, providing common
    attributes such as `jti` (JWT ID) and `realm`.

    Attributes:
        jti (str): The unique identifier for the token, generated as a UUID.
        realm (Realm): The realm associated with the token, represented as an Enum.
    """

    __abstract__ = True
    __cache_key_attr__ = "jti"

    jti = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    realm = Column(Enum(Realm), nullable=True)


class RefreshToken(Token):
    """
    Represents a refresh token.

    This class extends the `Token` class and includes additional attributes
    specific to refresh tokens, such as user ID, expiration details, and
    revocation status.

    Attributes:
       user_id (int): The ID of the user associated with the refresh token.
       revoked (bool): Indicates whether the refresh token has been revoked.
       issued_at (datetime): The timestamp when the refresh token was issued.
       expires_at (datetime): The timestamp when the refresh token expires.
       business_code (str): The code of the business associated with the refresh token.
       access_token (AccessToken): The associated access token, if any.
    """

    __tablename__ = "refresh_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.datetime.utcnow()
        + datetime.timedelta(days=int(config["REFRESH_TOKEN_EXPIRE_DAYS"]) or 14),
    )
    business_code = Column(String, ForeignKey("business.code"), nullable=True)
    access_token = relationship(
        "AccessToken", back_populates="refresh_token", uselist=False
    )

    def is_alive(self):
        """
        Check if the refresh token is still valid.

        A refresh token is considered valid if it has not been revoked and
        has not expired.

        Returns:
            bool: True if the refresh token is valid, False otherwise.
        """
        now = datetime.datetime.utcnow()  # noqa
        return self.expires_at > now and not self.revoked

    def __repr__(self):
        """
        Return a string representation of the RefreshToken instance.

        Returns:
            str: A string representation of the RefreshToken.
        """
        return f"<RefreshToken(jti='{self.jti}', user_id={self.user_id})>"


class AccessToken(Token):
    """
    Represents an access token.

    This class extends the `Token` class and includes additional attributes
    specific to access tokens, such as user ID, IP address, user agent,
    and revocation status.

    Attributes:
        user_id (int): The ID of the user associated with the access token.
        business_code (str): The code of the business associated with the access token.
        ip_addr (str): The IP address from which the access token was issued.
        user_agent (str): The user agent string from which the access token was issued.
        issued_at (datetime): The timestamp when the access token was issued.
        expires_at (datetime): The timestamp when the access token expires.
        revoked (bool): Indicates whether the access token has been revoked.
        refresh_token_jti (str): The JWT ID of the associated refresh token.
        refresh_token (RefreshToken): The associated refresh token, if any.
    """

    __tablename__ = "access_tokens"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_code = Column(String, ForeignKey("business.code"), nullable=True)
    ip_addr = Column(String, nullable=False)
    user_agent = Column(String, nullable=False, default="<unknown>")
    issued_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.datetime.utcnow()
        + datetime.timedelta(days=int(config["ACCESS_TOKEN_EXPIRE_DAYS"]) or 7),
    )
    revoked = Column(Boolean, nullable=False, default=False)
    refresh_token_jti = Column(String, ForeignKey("refresh_tokens.jti"), nullable=False)
    refresh_token = relationship(
        "RefreshToken", back_populates="access_token", uselist=False
    )

    @property
    def ip_address(self):
        """
        Get the IP address associated with the access token.

        Returns:
            str: The IP address from which the access token was issued.
        """
        return self.ip_addr

    def __eq__(self, other):
        """
        Check equality between two AccessToken instances.

        Two access tokens are considered equal if their JWT IDs (jti) are the same.

        Args:
            other (AccessToken): The other access token to compare against.

        Returns:
            bool: True if the tokens are equal, False otherwise.
        """
        return self.jti == other.jti

    def is_alive(self):
        """
        Check if the access token is still valid.

        An access token is considered valid if it has not been revoked and
        has not expired.

        Returns:
            bool: True if the access token is valid, False otherwise.
        """
        now = datetime.datetime.utcnow()  # noqa
        return self.expires_at > now and not self.revoked

    def __repr__(self):
        return (
            f"<AccessToken(jti='{self.jti}', user_id={self.user_id}, alive={self.is_alive()}, "
            f"refresh_jti='{self.refresh_token_jti})'>"
        )
