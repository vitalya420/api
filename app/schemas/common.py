from pydantic import field_validator

from app.utils import normalize_phone_number


class HasPhone:
    phone: str

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v):
        return normalize_phone_number(phone=v)
