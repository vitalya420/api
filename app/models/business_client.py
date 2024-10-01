from sqlalchemy import Column, Integer, ForeignKey, DateTime

from app.db import Base


class BusinessClient(Base):
    __tablename__ = 'business_client'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    business_id = Column(Integer, ForeignKey('business.id'))
    registration_date = Column(DateTime)
