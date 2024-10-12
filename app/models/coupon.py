from typing import Union

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.orm import Mapped, relationship

from app.const import COUPON_CODE_LENGTH, BUSINESS_CODE_LENGTH
from app.db import Base
from app.utils import random_code


class Coupon(Base):
    __tablename__ = "coupons"

    code: Mapped[str] = Column(
        String(COUPON_CODE_LENGTH),
        primary_key=True,
        default=lambda: random_code(COUPON_CODE_LENGTH),
    )
    client_id: Mapped[Union[int, None]] = Column(
        Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    used: Mapped[bool] = Column(Boolean, default=False)
    menu_position_id: Mapped[Union[int, None]] = Column(
        Integer, ForeignKey("menu_positions.id", ondelete="SET NULL"), nullable=True
    )
    business_code: Mapped[Union[str, None]] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    price: Mapped[float] = Column(Float, nullable=False, default=0.0)

    menu_position = relationship("MenuPosition", back_populates="coupons")
    client = relationship("Client", back_populates="coupons")
    business = relationship("Business", back_populates="issued_coupons")
