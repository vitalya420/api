from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.tokens import TokenPair


class ClientBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None


class ClientUpdateRequest(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int
    image: Optional[str] = None
    bonuses: float
    qr_code: str
    phone: str
    is_staff: bool
    created_at: str

    @field_validator("created_at", mode="before")  # noqa
    @classmethod
    def format_created_at(cls, value):
        return value.isoformat()

    @field_validator("image", mode="before")  # noqa
    @classmethod
    def set_image(cls, value):
        return value if value is not None else "default-image.png"

    class Config:
        from_attributes = True


class AuthorizedClientResponse(BaseModel):
    client: ClientResponse
    tokens: TokenPair

    class Config:
        from_attributes = True
