from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.db import Base


class OTP(Base):
    """
    Represents a One-Time Password (OTP) entry in the database.

    This model is used to store OTPs instead of using an in-memory store like Redis.
    Storing OTPs in the database allows for tracking and preventing abuse, as well as
    providing a persistent record of OTP generation and usage.

    Attributes:
        id (int): The unique identifier for the OTP entry (primary key).
        destination (str): The destination (e.g., phone number or email) where the OTP is sent.
        code (str): The actual OTP code that is generated and sent to the destination.
        sent_at (datetime): The timestamp indicating when the OTP was sent.
        expires_at (datetime): The timestamp indicating when the OTP will expire.
        used (int): A flag indicating whether the OTP has been used (0 for unused, 1 for used).

    Note:
        It is important to implement logic to handle OTP expiration and usage
        to ensure security and prevent abuse.
    """

    __tablename__ = 'otps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    destination = Column(String)
    code = Column(String)
    sent_at = Column(DateTime)
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)
    revoked = Column(Boolean, default=False)
