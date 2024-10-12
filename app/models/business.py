from typing import Union

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseCachableModel, BaseModelWithID
from app.const import BUSINESS_CODE_LENGTH, MAX_STRING_LENGTH
from app.utils import random_string_code


class BusinessFeedback(BaseModelWithID):
    __tablename__ = "business_feedbacks"

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

    def __repr__(self):
        return (
            f"<BusinessFeedback(client_id={self.client}, business_code={self.business_code}, "
            f"rating={self.rating}, comment={self.comment})>"
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

    bonus_logs = relationship(
        "BonusLog",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Business(code='{self.code}', name='{self.name}', owner_id={self.owner_id})>"
