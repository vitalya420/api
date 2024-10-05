from sqlalchemy import Column, Integer, String, ForeignKey

from app.db import Base
from app.utils.rand import random_business_code


class Business(Base):
    __tablename__ = 'business'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(12), nullable=False, index=True, default=random_business_code)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
