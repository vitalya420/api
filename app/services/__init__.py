from app.utils.registry import Registry
from .base import BaseService

services = Registry[BaseService]()

from .business import BusinessService
from .user import UserService
from .business_client import BusinessClient
from .auth import Authorization
from .tokens import TokenService

from app.db import async_session_factory

business = BusinessService(async_session_factory)
user = UserService(async_session_factory)
business_client = BusinessClient(async_session_factory)
auth = Authorization(async_session_factory)
tokens = TokenService(async_session_factory)
