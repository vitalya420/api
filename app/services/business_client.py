from .base import BaseService
from . import services


@services('business_client')
class BusinessClient(BaseService):

    def add_user_to_business(self, user_id: int, business_id: int):
        pass


