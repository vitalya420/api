from datetime import datetime
from typing import Union, List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, relationship

from app.base import BaseModelWithID
from app.const import BUSINESS_CODE_LENGTH, MAX_STRING_LENGTH, COUPON_CODE_LENGTH

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.business import Business


class BonusLog(BaseModelWithID):
    """
    Represents a log entry for bonus transactions associated with clients and businesses.

    Attributes:
        client_id (Union[int, None]): The ID of the client associated with the bonus transaction.
            This is a foreign key referencing the 'clients' table. It can be null if not applicable.
        business_code (Union[str, None]): The code of the business associated with the bonus transaction.
            This is a foreign key referencing the 'businesses' table. It can be null if not applicable.
        amount (float): The amount of the bonus transaction. Positive values indicate income, while
            negative values indicate an outcome (e.g., spending bonuses).
        reason (Union[str, None]): A description of the reason for the bonus transaction. This can be null.
        coupon_id (Union[int, None]): The code of the coupon associated with the bonus transaction, if applicable.
            This is a foreign key referencing the 'coupons' table. It can be null if not applicable.
        created_at (datetime): The timestamp when the bonus transaction was created. Defaults to the current UTC time.

    Relationships:
        client (List[Client]): A relationship to the Client model, allowing access to the client associated
            with this bonus log entry.
        business (List[Business]): A relationship to the Business model, allowing access to the business
            associated with this bonus log entry.
    """

    __tablename__ = "bonus_logs"

    client_id: Mapped[Union[int, None]] = Column(
        Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    business_code: Mapped[Union[str, None]] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[float] = Column(
        Float, nullable=False
    )  # if amount > 0 then income amount < 0 - outcome
    reason: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)
    # If bonuses were spent to get coupon
    coupon_id: Mapped[Union[int, None]] = Column(
        String(COUPON_CODE_LENGTH),
        ForeignKey("coupons.code", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)  # noqa

    client: Mapped[List["Client"]] = relationship("Client", back_populates="bonus_logs")
    business: Mapped[List["Business"]] = relationship(
        "Business", back_populates="bonus_logs"
    )
