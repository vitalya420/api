from sqlalchemy import Column, Integer, String

from app.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(32), nullable=False)
    last_name = Column(String(32), nullable=True)
    phone = Column(String(32), nullable=False)
