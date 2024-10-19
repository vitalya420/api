from datetime import time
from typing import Optional, List

from pydantic import BaseModel

from app.enums import DayOfWeek


class WorkScheduleDay(BaseModel):
    day: DayOfWeek
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
    schedule: List[WorkScheduleDay] = list()


class WorkScheduleUpdate(WorkScheduleCreate):
    disable: bool = False


class WorkScheduleCopy(BaseModel):
    establishment_id: int
