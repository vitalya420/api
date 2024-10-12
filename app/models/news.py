from typing import Union

from sqlalchemy import Column, String, Enum, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, relationship

from app.base import BaseModelWithIDAndDateTimeFields, BaseModelWithID
from app.const import (
    MAX_TITLE_NAME,
    MAX_NEWS_CONTENT_LENGTH,
    BUSINESS_CODE_LENGTH,
    MAX_STRING_LENGTH,
)
from app.enums import NewsContentType


class NewsView(BaseModelWithID):
    __tablename__ = "news_views"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_user_news"),)

    news_id: Mapped[int] = Column(Integer, ForeignKey("news.id"), nullable=False)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)

    news = relationship("News", back_populates="views")

    def __repr__(self):
        return f"<NewsView(news_id={self.news_id}, user_id={self.user_id})>"


class News(BaseModelWithIDAndDateTimeFields):
    __tablename__ = "news"

    title: Mapped[str] = Column(String(MAX_TITLE_NAME), nullable=False)
    content: Mapped[str] = Column(String(MAX_NEWS_CONTENT_LENGTH), nullable=False)
    content_type: Mapped[NewsContentType] = Column(
        Enum(NewsContentType), default=NewsContentType.plain
    )
    image: Mapped[Union[str, None]] = Column(String(MAX_STRING_LENGTH), nullable=True)
    business_code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="CASCADE"),
        nullable=False,
    )

    business = relationship("Business", back_populates="news")
    views = relationship(
        "NewsView", back_populates="news", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<News(title={self.title}, content={self.content})>"
