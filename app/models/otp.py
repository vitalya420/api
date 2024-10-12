from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped

from app.base import BaseModelWithID
from app.const import BUSINESS_CODE_LENGTH, MAX_PHONE_LENGTH, MAX_STRING_LENGTH
from app.enums import Realm


class OTP(BaseModelWithID):
    """
    Represents a One-Time Password (OTP) entry in the database.

    This model is used to store OTPs instead of using an in-memory store like Redis.
    Storing OTPs in the database allows for tracking and preventing abuse, as well as
    providing a persistent record of OTP generation and usage.

    Attributes:
        id (int): The unique identifier for the OTP entry (primary key).
        phone (str): The destination phone number where the OTP is sent. This can be null.
        business_code (str): The code of the business associated with the OTP. This is a foreign key
            referencing the 'businesses' table and can be null if not applicable.
        realm (Realm): The realm or context in which the OTP is used, represented as an enum.
        code (str): The actual OTP code that is generated and sent to the destination. This is a non-nullable string.
        sent_at (datetime): The timestamp indicating when the OTP was sent. This is a non-nullable datetime.
        expires_at (datetime): The timestamp indicating when the OTP will expire. This is a non-nullable datetime.
        used (bool): A flag indicating whether the OTP has been used. Defaults to False.
        revoked (bool): A flag indicating whether the OTP has been revoked. Defaults to False.

    Note:
        It is important to implement logic to handle OTP expiration and usage
        to ensure security and prevent abuse.

    Methods:
        __repr__() -> str: Returns a string representation of the OTP instance, indicating whether it is expired.
    """

    __tablename__ = "otps"

    phone: Mapped[str] = Column(String(MAX_PHONE_LENGTH), nullable=True)
    business_code: Mapped[str] = Column(
        String(BUSINESS_CODE_LENGTH),
        ForeignKey("businesses.code", ondelete="SET NULL"),
        nullable=True,
    )
    realm: Mapped[Realm] = Column(Enum(Realm), nullable=False)
    code: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=False)
    sent_at: Mapped[datetime] = Column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = Column(DateTime, nullable=False)
    used: Mapped[bool] = Column(Boolean, default=False)
    revoked: Mapped[bool] = Column(Boolean, default=False)

    def __repr__(self):
        now = datetime.utcnow()  # noqa
        expired = self.expires_at < now
        return f"<OTP(id={self.id}, destination='{self.phone}', code='{self.code}', expired={expired})>"
