from typing import Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.enums import Realm
from app.schemas.common import HasPhone


@openapi.component
class AuthRequest(BaseModel):
    phone: str
    realm: Realm
    password: Optional[str] = None
    business: Optional[str] = None


@openapi.component
class AuthConfirmRequest(BaseModel, HasPhone):
    phone: str
    otp: str
    business: str
