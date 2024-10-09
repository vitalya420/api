from pydantic import BaseModel, field_validator

from app.utils.phone import normalize_phone_number


class HasPhone(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v):
        return normalize_phone_number(phone=v)
