from app.utils.registry import Registry
from .base import BaseService

services = Registry[BaseService]()

from .business import BusinessService
from .user import UserService

