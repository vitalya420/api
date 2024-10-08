from typing import Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.schemas.enums import Realm


@openapi.component
class AuthRequest(BaseModel):
    phone: str
    realm: Realm
    password: Optional[str] = None
    business: Optional[str] = None
