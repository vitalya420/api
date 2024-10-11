from enum import Enum
from typing import Optional, List

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.schemas.business import BusinessResponse
from app.enums import Realm
from app.schemas.common import HasPhone


@openapi.component
class AuthMethod(str, Enum):
    password = "password"
    otp = "otp"


@openapi.component
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


@openapi.component
class UserCreate(BaseModel, HasPhone):
    pass


class User(UserBase):
    id: int


@openapi.component
class UserCodeConfirm(BaseModel, HasPhone):
    otp: str
    realm: Realm
    business: Optional[str] = None


@openapi.component
class WebUserResponse(BaseModel):
    phone: str
    businesses: List[BusinessResponse]

    class Config:
        from_attributes = True
