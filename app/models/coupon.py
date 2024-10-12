import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, String

from app.base import BaseModelWithID


class Coupon(BaseModelWithID):
    __tablename__ = 'coupons'

    menu_position = Column(Integer, ForeignKey('menu_positions.id'), nullable=False)
    creation_time = Column(DateTime, default=datetime.utcnow)  # noqa
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    business_code = Column(String, ForeignKey('business.code'), nullable=False)
