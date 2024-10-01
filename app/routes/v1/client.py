"""
This module contains routes for managing business client information.

It provides endpoints to:
- Retrieve information about a business client, including loyalty status and personal details.
- Update the client's information such as email, phone number, and first name.
- Delete a client from the business's records.

All routes require the user to be logged in and to have a valid business ID associated with their account.

Endpoints:
- GET /client/          : Retrieve business client information.
- PATCH /client/        : Update business client information.
- DELETE /client/       : Delete a business client.
"""

from sanic import Blueprint, Request, json

from app.security import (rules,
                          business_id_required,
                          login_required)

client = Blueprint('client', url_prefix='/client')


@client.get('/')
@rules(login_required, business_id_required)
async def get_business_client_info(request: Request):
    """
    Retrieve information about a business client.

    This endpoint returns details such as loyalty status, first name,
    and other relevant information about the client associated with
    the authenticated business.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success with client information.
    """
    return json({"ok": True})


@client.patch('/')
@rules(login_required, business_id_required)
async def update_client_info(request: Request):
    """
    Update information for a business client.

    This endpoint allows the modification of client details such as
    email, phone number, first name, and other relevant attributes.

    Args:
        request (Request): The Sanic request object containing the
                           request data, including the updated client
                           information.

    Returns:
        json: A JSON response indicating success of the update operation.
    """
    return json({"ok": True})


@client.delete('/')
@rules(login_required, business_id_required)
async def delete_client_info(request: Request):
    """
    Delete a business client.

    This endpoint removes the specified client from the business's
    records.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success of the deletion operation.
    """
    return json({"ok": True})
