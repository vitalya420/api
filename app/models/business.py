from sqlalchemy import Column, Integer, String

from app.db import Base


class Business(Base):
    __tablename__ = 'business'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(12), nullable=False, index=True)
    name = Column(String(255), nullable=False)
