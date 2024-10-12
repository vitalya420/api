import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Union

from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Enum,
    Integer,
    Boolean,
    DateTime,
    Float,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, relationship

from app.base import BaseCachableModel
from app.utils import random_string_code, random_code


class Realm(str, PyEnum):
    web = "web"
    mobile = "mobile"


class NewsContentType(str, PyEnum):
    plain = "plain"
    html = "html"
    markdown = "markdown"


class Currency(str, PyEnum):
    UAH = "UAH"
    USD = "USD"
    EUR = "EUR"


UUID_LENGTH = 36
BUSINESS_CODE_LENGTH = 16
COUPON_CODE_LENGTH = 16
USER_QR_CODE_LENGTH = 16
MAX_STRING_LENGTH = 128
MAX_PHONE_LENGTH = 18
MAX_PASSWORD_LENGTH = 72
MAX_TITLE_NAME = 20
MAX_NEWS_CONTENT_LENGTH = 512


class _BaseToken(BaseCachableModel):
    __abstract__ = True
    __cache_key_attr__ = "jti"

    jti: Mapped[str] = Column(
        String(UUID_LENGTH), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    realm: Mapped[Realm] = Column(Enum, nullable=False)
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


class RefreshToken(_BaseToken):
    __tablename__ = "refresh_tokens"
    type_str = "refresh"

    access_token_jti: Mapped[str] = Column(String(UUID_LENGTH), nullable=False)

    access_token = relationship(
        "AccessToken", foreign_keys=[access_token_jti], back_populates="refresh_token"
    )


class AccessToken(_BaseToken):
    __tablename__ = "access_tokens"
    type_str = "access"

    ip_address: Mapped[Union[str, None]] = Column(String, nullable=True)
    user_agent: Mapped[Union[str, None]] = Column(
        String(MAX_STRING_LENGTH), nullable=True
    )
    refresh_token_jti: Mapped[str] = Column(String(UUID_LENGTH), nullable=False)

    refresh_token = relationship(
        "RefreshToken", foreign_keys=[refresh_token_jti], back_populates="access_token"
    )


class User(BaseCachableModel):
    __tablename__ = "users"
    __cache_key_attr__ = ["id", "phone"]

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = Column(
        String(MAX_PHONE_LENGTH), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = Column(String(MAX_PASSWORD_LENGTH), nullable=True)
    is_admin: Mapped[bool] = Column(Boolean, default=False)

    business = relationship("Business", uselist=False, back_populates="owner")


class OTP(BaseCachableModel):
    __tablename__ = "otps"
    __cache_key_attr__ = "id"

    phone: Mapped[str] = Column(String(MAX_PHONE_LENGTH), nullable=True)
    business_code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    realm: Mapped[Realm] = Column(Enum(Realm), nullable=False)
    code: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=False)
    sent_at: Mapped[datetime] = Column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = Column(DateTime, nullable=False)
    used: Mapped[bool] = Column(Boolean, default=False)
    revoked: Mapped[bool] = Column(Boolean, default=False)


class MenuPosition(BaseCachableModel):
    __tablename__ = "menu_positions"
    __cache_key_attr__ = "id"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = Column(String(MAX_TITLE_NAME), nullable=False)
    description: Mapped[Union[str, None]] = Column(
        String(MAX_STRING_LENGTH), nullable=True
    )
    image: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)
    price: Mapped[float] = Column(Float, nullable=False, default=0.0)
    currency: Mapped[Currency] = Column(
        Enum(Currency), nullable=False, default=Currency.UAH
    )
    can_be_purchased_with_bonuses: Mapped[bool] = Column(Boolean, default=False)
    bonus_price: Mapped[float] = Column(Float, nullable=False, default=0.0)
    business_code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="CASCADE"),
        nullable=False,
    )

    business = relationship("Business", back_populates="menu_positions")
    coupons = relationship(
        "Coupon", back_populates="menu_position", cascade="all, delete-orphan"
    )


class Coupon(BaseCachableModel):
    __tablename__ = "coupons"

    code: Mapped[str] = Column(
        String(COUPON_CODE_LENGTH),
        primary_key=True,
        default=lambda: random_code(COUPON_CODE_LENGTH),
    )
    used: Mapped[bool] = Column(Boolean, default=False)
    menu_position_id: Mapped[Union[int, None]] = Column(
        Integer, ForeignKey("menu_positions.id", ondelete="SET NULL"), nullable=True
    )
    price: Mapped[float] = Column(Float, nullable=False, default=0.0)

    menu_position = relationship("MenuPosition", back_populates="coupons")
    business = relationship("Business", back_populates="issued_coupons")
    client = relationship("Client", back_populates="coupons")


class NewsView(BaseCachableModel):
    __tablename__ = "news_views"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_user_news"),)

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = Column(Integer, ForeignKey("news.id"), nullable=False)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)

    news = relationship("News", back_populates="views")
    user = relationship("User", back_populates="news_views")


class News(BaseCachableModel):
    __tablename__ = "news"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = Column(String(MAX_TITLE_NAME), nullable=False)
    content: Mapped[str] = Column(String(MAX_NEWS_CONTENT_LENGTH), nullable=False)
    content_type: Mapped[NewsContentType] = Column(
        Enum(NewsContentType), default=NewsContentType.plain
    )
    image: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)
    business_code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="CASCADE"),
        nullable=False,
    )

    business = relationship("Business", back_populates="news")
    views = relationship(
        "NewsView", back_populates="news", cascade="all, delete-orphan"
    )


class Business(BaseCachableModel):
    __tablename__ = "businesses"
    __cache_key_attr__ = "code"

    code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        primary_key=True,
        default=lambda: random_string_code(BUSINESS_CODE_LENGTH),
    )
    name: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=False)
    image: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=True)
    owner_id: Mapped[int] = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    owner = relationship("User", back_populates="business")
    menu_positions = relationship(
        "MenuPosition", back_populates="business", cascade="all, delete-orphan"
    )
    issued_coupons = relationship(
        "Coupon", back_populates="business", cascade="all, delete-orphan"
    )
    news = relationship("News", back_populates="business", cascade="all, delete-orphan")
    feedbacks = relationship(
        "BusinessFeedback", back_populates="business", cascade="all, delete-orphan"
    )

    bonus_logs: List["BonusLog"] = relationship(
        "BonusLog",
        back_populates="business",
        cascade="all, delete-orphan",
    )


class BusinessFeedback(BaseCachableModel):
    __tablename__ = "business_feedbacks"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = Column(
        Integer, ForeignKey("clients.id"), unique=True, nullable=False
    )
    business_code: Mapped[Union[str, None]] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    rating: Mapped[int] = Column(Integer, nullable=False)
    comment: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)

    client = relationship("Client", back_populates="feedback")
    business = relationship("Business", back_populates="feedbacks")


class Client(BaseCachableModel):
    __tablename__ = "clients"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Union[int, None]] = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    business_code: Mapped[Union[str, None]] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=False,
    )
    first_name: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=False)
    last_name: Mapped[Union[str, None]] = Column(
        String(MAX_STRING_LENGTH), nullable=True
    )
    bonuses: Mapped[float] = Column(Float, nullable=False, default=0.0)
    image: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)
    is_staff: Mapped[bool] = Column(Boolean, default=False)
    qr_code: Mapped[Union[str, None]] = Column(
        String(USER_QR_CODE_LENGTH),
        default=lambda: str(random_code(USER_QR_CODE_LENGTH)),
    )
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    coupons = relationship(
        "Coupon", back_populates="client", cascade="all, delete-orphan"
    )
    feedback = relationship(
        "BusinessFeedback",
        back_populates="client",
        uselist=False,
        cascade="all, delete-orphan",
    )

    bonus_logs: List["BonusLog"] = relationship(
        "BonusLog", back_populates="client", cascade="all, delete-orphan"
    )


class BonusLog(BaseCachableModel):
    __tablename__ = "bonus_logs"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[Union[int, None]] = Column(
        Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    business_code: Mapped[Union[str, None]] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[float] = Column(Float, nullable=False)
    reason: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)
    # If bonuses were spent to get coupon
    coupon_id: Mapped[Union[int, None]] = Column(
        String(COUPON_CODE_LENGTH),
        ForeignKey("coupons.code", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)  # noqa

    client = relationship("Client", back_populates="bonus_logs")
    business = relationship("Business", back_populates="bonus_logs")
