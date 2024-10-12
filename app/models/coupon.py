from typing import Union, TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.orm import Mapped, relationship

from app.const import COUPON_CODE_LENGTH, BUSINESS_CODE_LENGTH
from app.db import Base
from app.utils import random_code

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.business import Business
    from app.models.position import MenuPosition


class Coupon(Base):
    """
    Represents a coupon that can be issued to clients for use in a business.

    Attributes:
        code (str): A unique code identifying the coupon. This is the primary key and is generated
            using a random code.
        client_id (Union[int, None]): The ID of the client to whom the coupon is issued. This is a foreign key
            referencing the 'clients' table and can be null if not applicable.
        used (bool): A flag indicating whether the coupon has been used. Defaults to False.
        menu_position_id (Union[int, None]): The ID of the menu position associated with the coupon. This is a
            foreign key referencing the 'menu_positions' table and can be null if not applicable.
        business_code (Union[str, None]): The code of the business that issued the coupon. This is a foreign key
            referencing the 'businesses' table and can be null if not applicable.
        price (float): The price associated with the coupon. This is a non-nullable float, defaulting to 0.0.

    Relationships:
        menu_position (MenuPosition): A relationship to the MenuPosition model, allowing access to the menu position
            associated with the coupon.
        client (Client): A relationship to the Client model, allowing access to the client who holds the coupon.
        business (Business): A relationship to the Business model, allowing access to the business that issued the coupon.

    Methods:
        __repr__() -> str: Returns a string representation of the Coupon instance.
    """

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

    menu_position: Mapped["MenuPosition"] = relationship(
        "MenuPosition", back_populates="coupons"
    )
    client: Mapped["Client"] = relationship("Client", back_populates="coupons")
    business: Mapped["Business"] = relationship(
        "Business", back_populates="issued_coupons"
    )

    def __repr__(self):
        return (
            f"<Coupon(code='{self.code}', used='{self.used}', "
            f"client_id={self.client_id}, menu_position_id={self.menu_position_id})>"
        )
