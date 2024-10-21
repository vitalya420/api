from datetime import time
from typing import Union, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Time, Boolean, Integer
from sqlalchemy.orm import relationship, Mapped

from app.base import BaseModelWithID

if TYPE_CHECKING:
    from app.models.establisment import Establishment


class DayScheduleInfo(BaseModelWithID):
    __tablename__ = "day_schedule_infos"

    open_time: Mapped[Union[time, None]] = Column(Time, nullable=True)
    close_time: Mapped[Union[time, None]] = Column(Time, nullable=True)
    is_opened: Mapped[bool] = Column(Boolean, default=False)
    has_lunch_break: Mapped[bool] = Column(Boolean, default=False)
    lunch_break_start: Mapped[Union[time, None]] = Column(Time, nullable=True)
    lunch_break_end: Mapped[Union[time, None]] = Column(Time, nullable=True)

    def __repr__(self):
        return (
            f"<DayScheduleInfo("
            f"open_time={self.open_time}, close_time={self.close_time}, is_opened={self.is_opened}, "
            f"has_lunch_break={self.has_lunch_break}, lunch_break_start={self.lunch_break_start}, "
            f"lunch_break_end={self.lunch_break_end})>"
        )


class EstablishmentWorkSchedule(BaseModelWithID):
    __tablename__ = "establishment_work_schedules"

    establishment_id: Mapped[int] = Column(
        Integer, ForeignKey("establishments.id", ondelete="CASCADE"), nullable=False
    )
    monday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )
    tuesday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )
    wednesday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )
    thursday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )
    friday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )
    saturday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )
    sunday_id: Mapped[int] = Column(
        Integer, ForeignKey("day_schedule_infos.id"), nullable=False
    )

    monday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[monday_id]
    )
    tuesday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[tuesday_id]
    )
    wednesday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[wednesday_id]
    )
    thursday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[thursday_id]
    )
    friday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[friday_id]
    )
    saturday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[saturday_id]
    )
    sunday_schedule: Mapped["DayScheduleInfo"] = relationship(
        "DayScheduleInfo", foreign_keys=[sunday_id]
    )

    establishment: Mapped["Establishment"] = relationship(
        "Establishment", back_populates="work_schedule"
    )

    @property
    def monday(self):
        return self.monday_schedule

    @property
    def tuesday(self):
        return self.tuesday_schedule

    @property
    def wednesday(self):
        return self.wednesday_schedule

    @property
    def thursday(self):
        return self.thursday_schedule

    @property
    def friday(self):
        return self.friday_schedule

    @property
    def saturday(self):
        return self.saturday_schedule

    @property
    def sunday(self):
        return self.sunday_schedule
