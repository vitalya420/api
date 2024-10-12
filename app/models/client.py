from datetime import datetime
from typing import Union, TYPE_CHECKING, List

from sqlalchemy import Column, Integer, ForeignKey, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseCachableModelWithIDAndDateTimeFields
from app.utils import USER_QR_CODE_LENGTH, MAX_STRING_LENGTH, BUSINESS_CODE_LENGTH
from app.utils import random_code

if TYPE_CHECKING:
    from app.models.bonus_log import BonusLog
    from app.models.business import Business, BusinessFeedback
    from app.models.coupon import Coupon
    from app.models.user import User


class Client(BaseCachableModelWithIDAndDateTimeFields):
    """
    Represents a client within the system, associated with a business and potentially a user.

    Attributes:
        user_id (Union[int, None]): The ID of the user associated with the client. This is a foreign key
            referencing the 'users' table and can be null if not applicable.
        business_code (Union[str, None]): The code of the business associated with the client. This is a
            foreign key referencing the 'businesses' table and is non-nullable.
        first_name (str): The first name of the client. This is a non-nullable string.
        last_name (Union[str, None]): The last name of the client. This can be null.
        bonuses (float): The total bonuses available to the client. This is a non-nullable float, defaulting to 0.0.
        image (Union[str, None]): An optional URL or path to an image representing the client. This can be null.
        is_staff (bool): A flag indicating whether the client has staff privileges. Defaults to False.
        qr_code (Union[str, None]): A unique QR code for the client, generated using a random code. This can be null.
        deleted (bool): A flag indicating whether the client record is marked as deleted. Defaults to False.
        deleted_at (Union[datetime, None]): The timestamp when the client was marked as deleted. This can be null.

    Relationships:
        coupons (List[Coupon]): A relationship to the Coupon model, allowing access to the coupons associated
            with the client.
        feedback (BusinessFeedback): A relationship to the BusinessFeedback model, allowing access to the feedback
            provided by the client. This is a single instance (uselist=False).
        bonus_logs (List[BonusLog]): A relationship to the BonusLog model, allowing access to the bonus transaction
            logs associated with the client.

    Methods:
        get_key() -> str: Generates a unique key for the client based on the table name, user ID, and business code.
        __repr__() -> str: Returns a string representation of the Client instance.
    """

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
    deleted: Mapped[bool] = Column(Boolean, default=False)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)

    coupons: Mapped[List["Coupon"]] = relationship(
        "Coupon", back_populates="client", cascade="all, delete-orphan"
    )
    feedback: Mapped["BusinessFeedback"] = relationship(
        "BusinessFeedback",
        back_populates="client",
        uselist=False,
        cascade="all, delete-orphan",
    )

    bonus_logs: Mapped[List["BonusLog"]] = relationship(
        "BonusLog", back_populates="client", cascade="all, delete-orphan"
    )

    business: Mapped[List["Business"]] = relationship(
        "Business", foreign_keys=[business_code], back_populates="clients"
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    @property
    def phone(self):
        return self.user.phone

    def get_key(self) -> str:
        return f"{self.__tablename__}:{self.user_id}:{self.business_code}"

    def __repr__(self):
        return (
            f"<Client(business_code='{self.business_code}', user_id='{self.user_id}', "
            f"bonuses={self.bonuses}, is_staff={self.is_staff}>"
        )
