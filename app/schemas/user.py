from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(BaseModel):
    phone: str


class User(UserBase):
    id: int


class UserCodeConfirm(BaseModel):
    otp: str
    phone: str
