from typing import Union, TYPE_CHECKING, List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseCachableModel, BaseModelWithID
from app.utils import BUSINESS_CODE_LENGTH, MAX_STRING_LENGTH
from app.utils import random_string_code

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.bonus_log import BonusLog
    from app.models.news import News
    from app.models.coupon import Coupon
    from app.models.user import User
    from app.models.position import MenuPosition


class BusinessFeedback(BaseModelWithID):
    """
    Represents feedback provided by clients for a specific business.

    Attributes:
        client_id (int): The ID of the client providing the feedback. This is a foreign key referencing
            the 'clients' table and must be unique and non-nullable.
        business_code (Union[str, None]): The code of the business being reviewed. This is a foreign key
            referencing the 'businesses' table. It can be null if not applicable.
        rating (int): The rating given by the client for the business. This is a non-nullable integer.
        comment (Union[str, None]): An optional comment provided by the client regarding their experience.
            This can be null.

    Relationships:
        client (Client): A relationship to the Client model, allowing access to the client who provided
            the feedback.
        business (Business): A relationship to the Business model, allowing access to the business
            associated with this feedback entry.

    Methods:
        __repr__(): Returns a string representation of the BusinessFeedback instance.
    """

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

    client: Mapped["Client"] = relationship("Client", back_populates="feedback")
    business: Mapped["Business"] = relationship("Business", back_populates="feedbacks")

    def __repr__(self):
        return (
            f"<BusinessFeedback(client_id={self.client}, business_code={self.business_code}, "
            f"rating={self.rating}, comment={self.comment})>"
        )


class Business(BaseCachableModel):
    """
    Represents a business entity within the system.

    Attributes:
        code (str): A unique code identifying the business. This is the primary key and is generated
            using a random string code.
        name (str): The name of the business. This is a non-nullable string.
        image (Union[str, None]): An optional URL or path to an image representing the business.
            This can be null.
        owner_id (int): The ID of the user who owns the business. This is a foreign key referencing
            the 'users' table and must be unique and non-nullable.

    Relationships:
        owner (User): A relationship to the User model, allowing access to the owner of the business.
        menu_positions (List[MenuPosition]): A relationship to the MenuPosition model, allowing access
            to the menu items associated with the business.
        issued_coupons (List[Coupon]): A relationship to the Coupon model, allowing access to the coupons
            issued by the business.
        news (List[News]): A relationship to the News model, allowing access to news articles related to
            the business.
        feedbacks (List[BusinessFeedback]): A relationship to the BusinessFeedback model, allowing access
            to feedback entries provided by clients for the business.
        bonus_logs (List[BonusLog]): A relationship to the BonusLog model, allowing access to bonus
            transaction logs associated with the business.

    Methods:
        __repr__(): Returns a string representation of the Business instance.
    """

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

    owner: Mapped["User"] = relationship("User", back_populates="business")
    menu_positions: Mapped[List["MenuPosition"]] = relationship(
        "MenuPosition", back_populates="business", cascade="all, delete-orphan"
    )
    issued_coupons: Mapped[List["Coupon"]] = relationship(
        "Coupon", back_populates="business", cascade="all, delete-orphan"
    )
    news: Mapped[List["News"]] = relationship(
        "News", back_populates="business", cascade="all, delete-orphan"
    )
    feedbacks: Mapped[List["BusinessFeedback"]] = relationship(
        "BusinessFeedback", back_populates="business", cascade="all, delete-orphan"
    )

    bonus_logs: Mapped[List["BonusLog"]] = relationship(
        "BonusLog",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    clients: Mapped[List["Client"]] = relationship(
        "Client", back_populates="business", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Business(code='{self.code}', name='{self.name}', owner_id={self.owner_id})>"
