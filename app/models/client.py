from typing import Union

from sqlalchemy import Column, Integer, ForeignKey, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseCachableModelWithIDAndDateTimeFields
from app.const import USER_QR_CODE_LENGTH, MAX_STRING_LENGTH, BUSINESS_CODE_LENGTH
from app.utils import random_code


class Client(BaseCachableModelWithIDAndDateTimeFields):
    __tablename__ = "clients"

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

    bonus_logs = relationship(
        "BonusLog", back_populates="client", cascade="all, delete-orphan"
    )

    def get_key(self) -> str:
        return f"{self.__tablename__}:{self.user_id}:{self.business_code}"

    def __repr__(self):
        return (
            f"<Client(business_code='{self.business_code}', user_id='{self.user_id}', "
            f"bonuses={self.bonuses}, is_staff={self.is_staff}>"
        )
