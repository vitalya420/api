from sqlalchemy import Column, String, Enum, Text, Integer, ForeignKey

from app.base import BaseCachableModelWithIDAndDateTimeFields
from app.enums import NewsContentType


class News(BaseCachableModelWithIDAndDateTimeFields):
    __table__ = "news"

    title = Column(String(128), nullable=False)
    image = Column(String(128), nullable=True)
    content = Column(Text, nullable=True)
    content_type = Column(Enum(NewsContentType), default=NewsContentType.plain)
    views = Column(Integer, default=0)
    business_id = Column(Integer, ForeignKey('business.id'), nullable=False)