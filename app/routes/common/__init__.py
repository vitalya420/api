"""
This module defines common routes that are shared across all versions of the API.

It imports the `common_v1` Blueprint, which contains the routes for version 1,
and groups it under a new Blueprint with the URL prefix "/common". This allows
for a unified access point for common functionalities that may be utilized by
multiple API versions.

Modules included:
- common_v1: Contains the common routes for version 1 of the API.
"""

from sanic import Blueprint

from .v1 import common_v1

common_api = Blueprint.group(common_v1, url_prefix="/common")
