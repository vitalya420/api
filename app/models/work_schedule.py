from datetime import time
from typing import Union, TYPE_CHECKING

from sqlalchemy import Column, String, ForeignKey, Time, Boolean, Enum, Integer
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseModelWithID
from app.enums import DayOfWeek

if TYPE_CHECKING:
    from app.models.establisment import Establishment


class WorkSchedule(BaseModelWithID):
    """
    Represents the work schedule for a business.

    Attributes:
        establishment_id (str): The id of the establishment this schedule belongs to.
        day_of_week (DayOfWeek): The day of the week this schedule applies to.
        open_time (Union[time, None]): The time the business opens on this day.
        close_time (Union[time, None]): The time the business closes on this day.
        is_day_off (bool): Whether the business is closed on this day.
        has_lunch_break (bool): Whether the business has a lunch break on this day.
        lunch_break_start (Union[time, None]): The time the lunch break starts, if applicable.
        lunch_break_end (Union[time, None]): The time the lunch break ends, if applicable.
    """

    __tablename__ = "work_schedules"

    establishment_id: Mapped[int] = Column(
        Integer, ForeignKey("establishments.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[DayOfWeek] = Column(Enum(DayOfWeek), nullable=False)
    open_time: Mapped[Union[time, None]] = Column(Time, nullable=True)
    close_time: Mapped[Union[time, None]] = Column(Time, nullable=True)
    is_day_off: Mapped[bool] = Column(Boolean, default=False)
    has_lunch_break: Mapped[bool] = Column(Boolean, default=False)
    lunch_break_start: Mapped[Union[time, None]] = Column(Time, nullable=True)
    lunch_break_end: Mapped[Union[time, None]] = Column(Time, nullable=True)

    establishment: Mapped["Establishment"] = relationship(
        "Establishment", back_populates="work_schedules"
    )

    def __repr__(self):
        return (
            f"<WorkSchedule(establishment_id='{self.establishment_id}', day_of_week='{self.day_of_week}', "
            f"open_time={self.open_time}, close_time={self.close_time}, is_day_off={self.is_day_off}, "
            f"has_lunch_break={self.has_lunch_break}, lunch_break_start={self.lunch_break_start}, "
            f"lunch_break_end={self.lunch_break_end})>"
        )
