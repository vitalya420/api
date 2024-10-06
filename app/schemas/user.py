from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.utils.phone import normalize_phone_number


@openapi.component
class Realm(str, Enum):
    web = "web"
    mobile = "mobile"


class _HasPhone:
    phone: str

    def phone_normalize(self):
        return normalize_phone_number(phone=self.phone)


@openapi.component
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


@openapi.component
class UserCreate(BaseModel, _HasPhone):
    pass


class User(UserBase):
    id: int


@openapi.component
class UserCodeConfirm(BaseModel, _HasPhone):
    otp: str
    realm: Realm
    business: Optional[str] = None
