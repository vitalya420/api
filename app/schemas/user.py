from pydantic import BaseModel


class UserBase(BaseModel):
    phone: str


class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True


class WebUserResponse(BaseModel):
    user: UserResponse
