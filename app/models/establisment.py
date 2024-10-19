from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseModelWithID
from app.utils import MAX_STRING_LENGTH

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.work_schedule import WorkSchedule


class Address(BaseModelWithID):
    __tablename__ = "addresses"

    address: Mapped[str] = Column(String, primary_key=False)
    longitude: Mapped[float] = Column(Float, nullable=False)
    latitude: Mapped[float] = Column(Float, nullable=False)

    establishment: Mapped["Establishment"] = relationship(
        "Establishment", back_populates="address", uselist=False
    )

    def __repr__(self):
        return f"<Address(address='{self.address}', longitude={self.longitude}, latitude={self.latitude})>"


class Establishment(BaseModelWithID):
    __tablename__ = "establishments"

    name: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=False)
    image: Mapped[str] = Column(String(MAX_STRING_LENGTH), nullable=True)
    address_id: Mapped[Address] = Column(
        Integer, ForeignKey("addresses.id"), nullable=True
    )
    business_code: Mapped[str] = Column(
        String, ForeignKey("businesses.code", ondelete="CASCADE"), nullable=False
    )
    address: Mapped["Address"] = relationship(
        "Address", back_populates="establishment", uselist=False
    )
    business: Mapped["Business"] = relationship(
        "Business", back_populates="establishments"
    )
    work_schedules: Mapped[List["WorkSchedule"]] = relationship(
        "WorkSchedule", back_populates="establishment", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Establishment(name='{self.name}', address='{self.address}', business_code='{self.business_code}')>"
