from typing import Type

from .auth import auth, AuthorizationService
from .tokens import tokens, TokenService
from .user import user, UserService
from .base import BaseService

from app.utils.registry import Registry

services = Registry[Type[BaseService]](auth=AuthorizationService, tokens=TokenService, user=UserService)
