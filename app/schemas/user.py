from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    phone: str


class User(UserBase):
    id: int
