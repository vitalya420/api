from typing import List

from pydantic import BaseModel, model_validator
from typing_extensions import Optional

from app.schemas.work_schedule import WorkScheduleResponse


class EstablishmentBase(BaseModel):
    name: str


class EstablishmentCreate(BaseModel):
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def validate_coordinates(cls, values):
        longitude = values.get("longitude")
        latitude = values.get("latitude")

        if (longitude is None) != (latitude is None):
            values["longitude"] = None
            values["latitude"] = None

        return values


class EstablishmentUpdate(EstablishmentCreate):
    pass


class EstablishmentAddress(BaseModel):
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None

    class Config:
        from_attributes = True


class EstablishmentResponse(EstablishmentBase):
    id: int
    name: str
    image: Optional[str] = None
    address: Optional[EstablishmentAddress] = None
    work_schedule: Optional[WorkScheduleResponse] = None

    class Config:
        from_attributes = True


class EstablishmentsResponse(BaseModel):
    establishments: List[EstablishmentResponse] = list()

    class Config:
        from_attributes = True
