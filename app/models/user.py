import bcrypt
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.mixins import CachableModelWithIDMixin


class User(CachableModelWithIDMixin):
    __tablename__ = "users"
    __cache_key__ = "phone"

    phone = Column(String(32), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)

    businesses = relationship("Business", back_populates="owner")

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )

    def set_password(self, plain_password: str):
        self.password = bcrypt.hashpw(
            plain_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def __repr__(self):
        return f"<User(id={self.id}, phone='{self.phone}', is_admin='{self.is_admin}')>"
