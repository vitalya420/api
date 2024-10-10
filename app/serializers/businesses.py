from typing import List

from app.models import Business
from app.schemas.business import BusinessesResponse


def serialize_user_businesses(businesses: List[Business]):
    return BusinessesResponse.model_validate({"businesses": businesses}).model_dump()
