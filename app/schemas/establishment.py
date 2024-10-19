from typing import List

from pydantic import BaseModel
from typing_extensions import Optional


class EstablishmentBase(BaseModel):
    name: str


class EstablishmentCreate(EstablishmentBase):
    image: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


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

    class Config:
        from_attributes = True


class EstablishmentsResponse(BaseModel):
    establishments: List[EstablishmentResponse] = list()

    class Config:
        from_attributes = True
