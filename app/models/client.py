from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship

from app.base import BaseCachableModelWithIDAndDateTimeFields


class BusinessClient(BaseCachableModelWithIDAndDateTimeFields):
    """
    Represents a business entity.

    Attributes:
        code (str): The unique code of the business.
        name (str): The name of the business.
        picture (str): The URL of the business's picture (optional).
        owner_id (int): The ID of the user who owns the business.
    """

    __tablename__ = "clients"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_code = Column(String, ForeignKey("business.code"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    picture = Column(String)
    bonuses = Column(Float, default=0.0)

    business = relationship(
        "Business", back_populates="clients", uselist=False
    )  # client can have one business
