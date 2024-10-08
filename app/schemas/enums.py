from enum import Enum

from sanic_ext.extensions.openapi import openapi


@openapi.component
class Realm(str, Enum):
    web = "web"
    mobile = "mobile"
