from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.mixins import CacheableModelMixin


class User(CacheableModelMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(32), nullable=False, unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    creation_time = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, phone='{self.phone}', is_admin='{self.is_admin}')>"
