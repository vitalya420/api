from datetime import time
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.enums import DayOfWeek


def _validate_time(value):
    if isinstance(value, str) and ':' in value:
        hours, minutes = value.split(':')
        return time(int(hours), int(minutes))
    return None


class WorkScheduleDay(BaseModel):
    is_opened: bool
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    has_lunch_break: Optional[bool] = None
    lunch_break_start: Optional[time] = None
    lunch_break_end: Optional[time] = None

    @field_validator("open_time", mode="before")  # noqa
    @classmethod
    def format_open_time(cls, value):
        return _validate_time(value)

    @field_validator("close_time", mode="before")  # noqa
    @classmethod
    def format_open_time(cls, value):
        return _validate_time(value)

    @field_validator("lunch_break_start", mode="before")  # noqa
    @classmethod
    def format_open_time(cls, value):
        return _validate_time(value)

    @field_validator("lunch_break_end", mode="before") # noqa
    @classmethod
    def format_open_time(cls, value):
        return _validate_time(value)

    @property
    def is_day_off(self):
        return not self.is_opened


class WorkScheduleCreate(BaseModel):
    monday: WorkScheduleDay
    tuesday: WorkScheduleDay
    wednesday: WorkScheduleDay
    thursday: WorkScheduleDay
    friday: WorkScheduleDay
    saturday: WorkScheduleDay
    sunday: WorkScheduleDay


class WorkScheduleUpdate(WorkScheduleCreate):
    disable: bool = False


class WorkScheduleCopy(BaseModel):
    establishment_id: int
