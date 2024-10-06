from sqlalchemy import Column, Integer, String, ForeignKey

from app.mixins.model import CacheableModelMixin
from app.utils.rand import random_business_code


class Business(CacheableModelMixin):
    __tablename__ = "business"

    code = Column(String(12), primary_key=True, default=random_business_code)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    def get_key(self) -> str:
        return f"{self.__tablename__}:{self.code}"

    def __repr__(self):
        return f"<Business(id={self.id}, code='{self.code}', name='{self.name}')>"
