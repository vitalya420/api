from typing import List

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi


@openapi.component
class BusinessCreate(BaseModel):
    name: str
    owner_id: int


@openapi.component
class Business(BaseModel):
    code: str
    name: str


@openapi.component
class BusinessResponse(Business):
    class Config:
        from_attributes = True


@openapi.component
class BusinessesResponse(BaseModel):
    businesses: List[BusinessResponse]

    class Config:
        from_attributes = True
