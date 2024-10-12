from pydantic import BaseModel


class _HasBusiness:
    business: str

    @property
    def business_code(self):
        return self.business


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = ""
