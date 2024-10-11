import bcrypt
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.base import BaseCachableModelWithID


class User(BaseCachableModelWithID):
    """
    Represents a user in the system.

    This class defines the user model, including attributes for phone number,
    password, and admin status. It also establishes relationships with other
    models, such as businesses owned by the user.

    Attributes:
        phone (str): The user's phone number, which must be unique.
        password (str): The hashed password of the user (optional).
        is_admin (bool): Indicates whether the user has admin privileges (default is False).
        businesses (List[Business]): A list of businesses owned by the user.
    """

    __tablename__ = "users"
    __cache_key_attr__ = [
        "id",
        "phone",
    ]  # id is main key and phone is reference to "users:<that id>"

    phone = Column(String(32), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)

    businesses = relationship("Business", back_populates="owner")
    clients = relationship("BusinessClient", back_populates="user")

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
