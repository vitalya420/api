from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.base import BaseCachableModel
from app.utils.rand import random_business_code


class Business(BaseCachableModel):
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

    __tablename__ = "business"
    __cache_key_attr__ = "code"

    code = Column(String(12), primary_key=True, default=random_business_code)
    name = Column(String(255), nullable=False)
    picture = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="businesses")
    clients = relationship(
        "BusinessClient", back_populates="business"
    )  # business can have a lot of clients

    def __repr__(self):
        return f"<Business(code='{self.code}', name='{self.name}', owner_id={self.owner_id})>"
