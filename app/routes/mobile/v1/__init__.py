"""
This module contains routes for the mobile API version 1.

It imports and groups the client and business-related routes into a single
Blueprint for better organization and management. The routes are prefixed with
"/v1" to indicate that they belong to version 1 of the mobile API.

Modules included:
- client: Handles routes related to client functionalities.
- business: Manages routes associated with business operations.
"""

from sanic import Blueprint

from .client import client
from .business import business

blueprints = (client, business)

mobile_api_v1 = Blueprint.group(*blueprints, url_prefix="v1")
