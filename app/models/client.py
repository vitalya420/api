from sqlalchemy import Column, Integer, ForeignKey

from app.mixins.model import CacheableModelMixin


class BusinessClient(CacheableModelMixin):
    __tablename__ = 'business_client'

    user_id = Column(Integer, ForeignKey('users.id'))
    business_id = Column(Integer, ForeignKey('business.id'))

