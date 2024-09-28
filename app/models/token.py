import datetime
import uuid

from sqlalchemy import (Column, String, Integer,
                        ForeignKey, DateTime, Boolean)
from sqlalchemy.orm import relationship

from app.config import config
from app.db import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    jti = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(
        days=config.REFRESH_TOKEN_EXPIRE_DAYS or 14))
    # access_token = relationship("AccessToken", back_populates="refresh_token")


class AccessToken(Base):
    __tablename__ = 'access_tokens'

    jti = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ip_addr = Column(String, nullable=False)
    user_agent = Column(String, nullable=False, default='<unknown>')
    issued_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.datetime.utcnow() + datetime.timedelta(
        days=config.ACCESS_TOKEN_EXPIRE_DAYS or 7))
    revoked = Column(Boolean, nullable=False, default=False)
    # refresh_token = relationship("RefreshToken", back_populates="access_token")
