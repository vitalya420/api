from typing import TYPE_CHECKING

import bcrypt
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseCachableModelWithID
from app.const import MAX_PHONE_LENGTH, MAX_PASSWORD_LENGTH

if TYPE_CHECKING:
    from app.models.business import Business


class User(BaseCachableModelWithID):
    """
    Represents a user in the system, associated with a phone number and optional business ownership.

    Attributes:
        phone (str): The phone number of the user. This is a non-nullable, unique string indexed for quick lookup.
        password (str): The hashed password of the user. This can be null if not set.
        is_admin (bool): A flag indicating whether the user has administrative privileges. Defaults to False.

    Relationships:
        business (Business): A relationship to the Business model, allowing access to the business owned by the user.
        This is a single instance (uselist=False).

    Methods:
        check_password(plain_password: str) -> bool: Checks if the provided plain password matches the stored hashed password.
        set_password(plain_password: str): Sets the user's password by hashing the provided plain password.
        __eq__(other) -> bool: Compares this user instance with another for equality based on user ID.
        __repr__() -> str: Returns a string representation of the User instance, including its ID, phone number, and admin status.
    """

    __tablename__ = "users"
    __cache_key_attr__ = ["id", "phone"]

    phone: Mapped[str] = Column(
        String(MAX_PHONE_LENGTH), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = Column(String(MAX_PASSWORD_LENGTH), nullable=True)
    is_admin: Mapped[bool] = Column(Boolean, default=False)

    business: Mapped["Business"] = relationship(
        "Business", uselist=False, back_populates="owner"
    )

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
