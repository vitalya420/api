from datetime import datetime
from typing import Union

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, relationship

from app.base import BaseModelWithID
from app.const import BUSINESS_CODE_LENGTH, MAX_STRING_LENGTH, COUPON_CODE_LENGTH


class BonusLog(BaseModelWithID):
    __tablename__ = "bonus_logs"

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
