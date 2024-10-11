from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship

from app.base import BaseCachableModelWithIDAndDateTimeFields


class BusinessClient(BaseCachableModelWithIDAndDateTimeFields):
    """
    Represents a client associated with a business.

    Attributes:
        user_id (int): The ID of the user associated with the client.
        business_code (str): The code of the business the client is associated with.
        first_name (str): The first name of the client.
        last_name (str): The last name of the client (optional).
        picture (str): The URL of the client's picture (optional).
        bonuses (float): The bonuses associated with the client (default is 0.0).
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
