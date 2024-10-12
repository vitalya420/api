from sqlalchemy import Column, Integer, String, ForeignKey

from app.base import BaseModelWithID


class BonusLog(BaseModelWithID):
    __table__ = 'bonus_logs'

    amount = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
