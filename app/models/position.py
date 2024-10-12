from typing import Union

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, relationship

from app.base import BaseModelWithID
from app.const import MAX_TITLE_NAME, MAX_STRING_LENGTH, BUSINESS_CODE_LENGTH
from app.enums import Currency


class MenuPosition(BaseModelWithID):
    __tablename__ = "menu_positions"
    __cache_key_attr__ = "id"

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
