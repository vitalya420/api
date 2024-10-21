"""
This module contains the API for the web interface version 1.

It imports and groups the user and business-related routes into a single
Blueprint for better organization and management. The routes are prefixed with
"/v1" to indicate that they belong to version 1 of the web API.

Modules included:
- user: Handles routes related to user functionalities, such as authentication
  and user management.
- business: Manages routes associated with business operations and related
  functionalities.
"""

from sanic import Blueprint

from .user import user
from .business import business
from .establishment import establishment

blueprints = (user, business, establishment)

web_api_v1 = Blueprint.group(*blueprints, url_prefix="/v1")
