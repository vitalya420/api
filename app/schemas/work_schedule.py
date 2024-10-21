from datetime import time
from typing import Optional

from pydantic import BaseModel, field_validator


class WorkScheduleDay(BaseModel):
    is_opened: bool
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    has_lunch_break: Optional[bool] = None
    lunch_break_start: Optional[time] = None
    lunch_break_end: Optional[time] = None

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


class WorkScheduleDayResponse(BaseModel):
    is_opened: bool
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    has_lunch_break: bool
    lunch_break_start: Optional[str] = None
    lunch_break_end: Optional[str] = None

    @classmethod
    def _strify_time(cls, value: Optional[time]) -> Optional[str]:
        """Convert time object to string in HH:MM format."""
        if isinstance(value, time):
            return value.strftime("%H:%M")
        return value

    @field_validator(
        "open_time", "close_time", "lunch_break_start", "lunch_break_end", mode="before"
    )  # noqa
    @classmethod
    def strify_time_fields(cls, value, field):
        """Convert time fields to string format if they are time objects."""
        return cls._strify_time(value)

    @field_validator("has_lunch_break", mode="before")  # noqa
    @classmethod
    def ensure_lunch_break_default(cls, value):
        """Ensure has_lunch_break defaults to False if not provided."""
        return value if value is not None else False

    class Config:
        from_attributes = True


class WorkScheduleResponse(BaseModel):
    monday: WorkScheduleDayResponse
    tuesday: WorkScheduleDayResponse
    wednesday: WorkScheduleDayResponse
    thursday: WorkScheduleDayResponse
    friday: WorkScheduleDayResponse
    saturday: WorkScheduleDayResponse
    sunday: WorkScheduleDayResponse

    class Config:
        from_attributes = True


class WorkScheduleUpdate(WorkScheduleCreate):
    disable: bool = False


class WorkScheduleCopy(BaseModel):
    establishment_id: int
