from typing import Optional

from pydantic import BaseModel

from app.utils.phone import normalize_phone_number


class _HasPhone:
    phone: str

    def phone_normalize(self):
        return normalize_phone_number(phone=self.phone)


class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(BaseModel, _HasPhone):
    phone: str


class User(UserBase):
    id: int


class UserCodeConfirm(BaseModel, _HasPhone):
    otp: str
    phone: str
