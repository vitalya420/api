from typing import Union, TYPE_CHECKING

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

if TYPE_CHECKING:
    from app.models.business import Business


class NewsView(BaseModelWithID):
    """
    Represents a view of a news article by a user.

    Attributes:
        news_id (int): The ID of the news article that was viewed. This is a foreign key referencing
            the 'news' table and is non-nullable.
        user_id (int): The ID of the user who viewed the news article. This is a foreign key referencing
            the 'users' table and is non-nullable.

    Relationships:
        news (News): A relationship to the News model, allowing access to the news article that was viewed.

    Methods:
        __repr__() -> str: Returns a string representation of the NewsView instance.
    """

    __tablename__ = "news_views"
    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_user_news"),)

    news_id: Mapped[int] = Column(Integer, ForeignKey("news.id"), nullable=False)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)

    news: Mapped["News"] = relationship("News", back_populates="views")

    def __repr__(self):
        return f"<NewsView(news_id={self.news_id}, user_id={self.user_id})>"


class News(BaseModelWithIDAndDateTimeFields):
    """
    Represents a news article associated with a business.

    Attributes:
        title (str): The title of the news article. This is a non-nullable string.
        content (str): The content of the news article. This is a non-nullable string.
        content_type (NewsContentType): The type of content for the news article, represented as an enum.
            Defaults to NewsContentType.plain.

        image (Union[str, None]): An optional URL or path to an image associated with the news article. This can be null.
        business_code (str): The code of the business associated with the news article. This is a foreign key
            referencing the 'businesses' table and is non-nullable.

    Relationships:
        business (Business): A relationship to the Business model, allowing access to the business that published the news.
        views (List[NewsView]): A relationship to the NewsView model, allowing access to the views of the news article.

    Methods:
        __repr__() -> str: Returns a string representation of the News instance.
    """

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

    business: Mapped["Business"] = relationship("Business", back_populates="news")
    views: Mapped["NewsView"] = relationship(
        "NewsView", back_populates="news", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<News(title={self.title}, content={self.content})>"
