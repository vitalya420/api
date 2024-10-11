from typing import Optional

from pydantic import BaseModel
from sanic_ext.extensions.openapi import openapi

from app.schemas.tokens import TokenPair
from app.schemas.user import WebUserResponse


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""
