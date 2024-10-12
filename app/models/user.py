import bcrypt
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseCachableModelWithID
from app.const import MAX_PHONE_LENGTH, MAX_PASSWORD_LENGTH


class User(BaseCachableModelWithID):
    __tablename__ = "users"
    __cache_key_attr__ = ["id", "phone"]

    phone: Mapped[str] = Column(
        String(MAX_PHONE_LENGTH), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = Column(String(MAX_PASSWORD_LENGTH), nullable=True)
    is_admin: Mapped[bool] = Column(Boolean, default=False)

    business = relationship("Business", uselist=False, back_populates="owner")

    def check_password(self, plain_password: str) -> bool:
        """
        Check if the provided plain password matches the stored hashed password.

        Args:
            plain_password (str): The plain text password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )

    def set_password(self, plain_password: str):
        """
        Set the user's password by hashing the provided plain password.

        Args:
            plain_password (str): The plain text password to set.
        """
        self.password = bcrypt.hashpw(
            plain_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"<User(id={self.id}, phone='{self.phone}', is_admin='{self.is_admin}')>"
