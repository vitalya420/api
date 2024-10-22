from typing import Optional, List

from pydantic import BaseModel

from app.schemas.client import ClientResponse
from app.schemas.establishment import EstablishmentResponse
from app.schemas.pagination import PaginatedResponse


class BusinessBase(BaseModel):
    name: str
    code: str
    owner_id: int
    description: Optional[str] = None
    image: Optional[str] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class BusinessCreate(BaseModel):
    name: str
    owner_id: Optional[int] = None
    owner_phone: Optional[str] = None


class BusinessResponse(BusinessBase):
    establishments: List[EstablishmentResponse] = list()

    class Config:
        from_attributes = True


class ListBusinessClientResponse(PaginatedResponse):
    clients: List[ClientResponse]

    class Config:
        from_attributes = True
