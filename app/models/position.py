from typing import Union, TYPE_CHECKING, List

from sqlalchemy import Column, String, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, relationship

from app.base import BaseModelWithID
from app.const import MAX_TITLE_NAME, MAX_STRING_LENGTH, BUSINESS_CODE_LENGTH
from app.enums import Currency
from app.models import Coupon

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.coupon import Coupon


class MenuPosition(BaseModelWithID):
    """
    Represents a menu item within a business's offerings.

    Attributes:
        title (str): The title of the menu position. This is a non-nullable string.
        description (Union[str, None]): An optional description of the menu position. This can be null.
        image (Union[str, None]): An optional URL or path to an image representing the menu position. This can be null.
        price (float): The price of the menu position. This is a non-nullable float, defaulting to 0.0.
        currency (Currency): The currency in which the price is specified, represented as an enum. Defaults to Currency.UAH.
        can_be_purchased_with_bonuses (bool): A flag indicating whether the menu position can be purchased using bonuses. Defaults to False.
        bonus_price (float): The price of the menu position when purchased with bonuses. This is a non-nullable float, defaulting to 0.0.
        business_code (str): The code of the business that offers this menu position. This is a foreign key referencing the 'businesses' table and is non-nullable.

    Relationships:
        business (Business): A relationship to the Business model, allowing access to the business that offers this menu position.
        coupons (List[Coupon]): A relationship to the Coupon model, allowing access to the coupons associated with this menu position.

    Methods:
        __repr__() -> str: Returns a string representation of the MenuPosition instance, including its title, price, currency, and bonus purchase options.
    """

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

    business: Mapped["Business"] = relationship(
        "Business", back_populates="menu_positions"
    )
    coupons: Mapped[List["Coupon"]] = relationship(
        "Coupon", back_populates="menu_position", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<MenuPosition(title={self.title}, price={self.price}, currency={self.currency}, "
            f"can_be_purchased_with_bonuses={self.can_be_purchased_with_bonuses},"
            f"bonus_price={self.bonus_price})>"
        )
