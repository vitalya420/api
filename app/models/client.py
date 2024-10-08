from sqlalchemy import Column, Integer, ForeignKey, String

from app.mixins.model import CachableModelWithDateTimeFieldsMixin


class BusinessClient(CachableModelWithDateTimeFieldsMixin):
    __tablename__ = "clients"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_code = Column(String, ForeignKey("business.code"), nullable=False)
