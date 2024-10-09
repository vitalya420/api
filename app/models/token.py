import datetime
import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum

from app.config import config
from app.schemas.user import Realm
from app.base import BaseCachableModel


class Token(BaseCachableModel):
    __abstract__ = True
    __cache_key_attr__ = "jti"

    jti = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    realm = Column(Enum(Realm), nullable=True)


class RefreshToken(Token):
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

    def is_alive(self):
        now = datetime.datetime.utcnow()
        return self.expires_at > now and not self.revoked

    def __repr__(self):
        return f"<RefreshToken(jti='{self.jti}', user_id={self.user_id})>"


class AccessToken(Token):
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

    @property
    def ip_address(self):
        return self.ip_addr

    def __eq__(self, other):
        return self.jti == other.jti

    def is_alive(self):
        now = datetime.datetime.utcnow()
        return self.expires_at > now and not self.revoked

    def __repr__(self):
        return (
            f"<AccessToken(jti='{self.jti}', user_id={self.user_id}, alive={self.is_alive()}, "
            f"refresh_jti='{self.refresh_token_jti})'>"
        )
