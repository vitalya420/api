from typing import List, Optional

from pydantic import BaseModel, field_validator
from sanic_ext.extensions.openapi import openapi

from app.schemas.response import SuccessResponse
from app.utils import normalize_phone_number


@openapi.component
class BusinessCreate(BaseModel):
    name: str
    owner_id: Optional[int] = None
    owner_phone: Optional[str] = None

    @field_validator("owner_phone")
    @classmethod
    def normalize_phone(cls, v):
        if v:
            return normalize_phone_number(phone=v)


@openapi.component
class Business(BaseModel):
    code: str
    name: str
    picture: Optional[str] = None
    owner_id: int


@openapi.component
class BusinessResponse(Business):
    class Config:
        from_attributes = True


@openapi.component
class BusinessesResponse(BaseModel):
    businesses: List[BusinessResponse]

    class Config:
        from_attributes = True


@openapi.component
class BusinessCreationResponse(SuccessResponse):
    business: BusinessResponse

    class Config:
        from_attributes = True
