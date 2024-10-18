"""
This module defines common routes for version 1 of the API.

It imports and groups the authentication and token-related routes into a single
Blueprint for easier management and organization. The routes are prefixed with
"/v1" to indicate that they belong to version 1 of the API.

Modules included:
- auth: Handles user authentication routes.
- tokens: Manages token generation and validation routes.
"""

from sanic import Blueprint

from .auth import auth
from .tokens import tokens
from .upload import file_upload

blueprint = (auth, tokens, file_upload)

common_v1 = Blueprint.group(*blueprint, url_prefix="/v1")
