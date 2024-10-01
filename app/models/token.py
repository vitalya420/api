import datetime
import uuid

from sqlalchemy import (Column, String, Integer,
                        ForeignKey, DateTime, Boolean)

from app.config import config
from app.db import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    jti = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(
        days=int(config['REFRESH_TOKEN_EXPIRE_DAYS']) or 14))
    business = Column(String)

    # access_token_jti = Column(String, ForeignKey('access_tokens.jti'), nullable=False)

    def __repr__(self):
        return f"<RefreshToken(jti='{self.jti}', user_id={self.user_id})>"


class AccessToken(Base):
    __tablename__ = 'access_tokens'

    jti = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    business = Column(String)
    ip_addr = Column(String, nullable=False)
    user_agent = Column(String, nullable=False, default='<unknown>')
    issued_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(
        days=int(config['ACCESS_TOKEN_EXPIRE_DAYS']) or 7))
    revoked = Column(Boolean, nullable=False, default=False)
    refresh_token_jti = Column(String, ForeignKey('refresh_tokens.jti'), nullable=False)

    @property
    def ip_address(self):
        return self.ip_addr

    def __eq__(self, other):
        return self.jti == other.jti

    def __repr__(self):
        return f"<AccessToken(jti='{self.jti}', user_id={self.user_id}), refresh_jti='{self.refresh_token_jti}'>"
