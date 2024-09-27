from .base import BaseService
from . import services


@services("business")
class BusinessService(BaseService):
    pass
