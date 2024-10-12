from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey

from app.base import BaseModelWithID


class MenuPosition(BaseModelWithID):
    __table__ = 'menu_positions'

    name = Column(String(18), primary_key=True)
    description = Column(String(255))
    image = Column(String(128), nullable=True)
    price = Column(Float, nullable=True)
    can_be_purchased_with_bonuses = Column(Boolean, nullable=False, default=False)
    bonus_price = Column(Float, nullable=True)
    business_id = Column(Integer, ForeignKey('business.id'), nullable=False)
