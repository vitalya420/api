from typing import Optional, List

from pydantic import BaseModel

from app.schemas.client import ClientResponse
from app.schemas.pagination import PaginatedResponse


class BusinessBase(BaseModel):
    name: str
    code: str
    owner_id: int


class BusinessCreate(BaseModel):
    name: str
    owner_id: Optional[int] = None
    owner_phone: Optional[str] = None


class BusinessResponse(BusinessBase):
    class Config:
        from_attributes = True


class ListBusinessClientResponse(PaginatedResponse):
    clients: List[ClientResponse]

    class Config:
        from_attributes = True
