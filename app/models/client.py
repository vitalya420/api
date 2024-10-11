from sqlalchemy import Column, Integer, ForeignKey, String, Float, Boolean
from sqlalchemy.orm import relationship

from app.base import BaseCachableModelWithIDAndDateTimeFields
from app.utils import random_code


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

    __cache_key_attr__ = "user_id"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_code = Column(String, ForeignKey("business.code"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    picture = Column(String)
    bonuses = Column(Float, default=0.0)
    is_staff = Column(Boolean, default=False)
    qr_code = Column(String, nullable=True, default=lambda: str(random_code(10)))

    business = relationship(
        "Business", back_populates="clients", uselist=False
    )  # client can have one business
    user = relationship("User", back_populates="clients", uselist=False)

    @property
    def phone(self):
        return self.user.phone

    @property
    def business_name(self):
        return self.business.name

    def get_key(self) -> str:
        return f"{self.__tablename__}:{self.user_id}:{self.business_code}"

    def __repr__(self):
        return (
            f"<BusinessClient(business_code='{self.business_code}', "
            f"user_id='{self.user_id}', bonuses={self.bonuses}, is_staff={self.is_staff}>"
        )
