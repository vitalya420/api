from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.base import BaseCachableModel
from app.utils import random_string_code


class Business(BaseCachableModel):
    """
    Represents a business entity.

    Attributes:
        code (str): The unique code of the business.
        name (str): The name of the business.
        picture (str): The URL of the business's picture (optional).
        owner_id (int): The ID of the user who owns the business.
    """

    __tablename__ = "business"
    __cache_key_attr__ = "code"

    code = Column(String(12), primary_key=True, default=random_string_code)
    name = Column(String(255), nullable=False)
    picture = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="businesses")
    clients = relationship(
        "BusinessClient", back_populates="business"
    )  # business can have a lot of clients

    def __repr__(self):
        return f"<Business(code='{self.code}', name='{self.name}', owner_id={self.owner_id})>"
