import datetime
import uuid
from typing import Union

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped

from app.base import BaseCachableModel
from app.const import UUID_LENGTH, BUSINESS_CODE_LENGTH, MAX_STRING_LENGTH
from app.enums import Realm


class _BaseToken(BaseCachableModel):
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
    __tablename__ = "refresh_tokens"
    type_str = "refresh"

    access_token_jti: Mapped[Union[str, None]] = Column(
        String(UUID_LENGTH), ForeignKey("access_tokens.jti"), nullable=True
    )

    def __repr__(self):
        return f"<RefreshToken(jti='{self.jti}', realm={self.realm}, user_id={self.user_id}, alive={self.is_alive()})>"


class AccessToken(_BaseToken):
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
