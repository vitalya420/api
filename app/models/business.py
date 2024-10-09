from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.mixins.model import CachableModelNoFieldsMixin
from app.utils.rand import random_business_code


class Business(CachableModelNoFieldsMixin):
    __tablename__ = "business"
    __cache_key__ = "code"

    code = Column(String(12), primary_key=True, default=random_business_code)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="businesses")

    def __repr__(self):
        return f"<Business(code='{self.code}', name='{self.name}', owner_id={self.owner_id})>"
