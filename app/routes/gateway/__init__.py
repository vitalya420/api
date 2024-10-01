"""
This module contains routes for the WebSocket gateway.

It provides endpoints to:
- Retrieve the endpoint for the WebSocket gateway.
- Handle WebSocket connections and messages.

Endpoints:
- GET /gateway/endpoint      : Returns the endpoint for the WebSocket gateway.
- WebSocket /gateway/        : Handles WebSocket connections and message exchanges.
"""

from sanic import Blueprint, Request, json, Websocket

gateway = Blueprint('gateway', url_prefix='/gateway')


@gateway.route('/endpoint')
async def get_endpoint(request: Request):
    """
    Retrieve the endpoint for the WebSocket gateway.

    This endpoint returns a JSON response indicating the availability
    of the WebSocket gateway.

    Args:
        request (Request): The Sanic request object containing the
                           request data.

    Returns:
        json: A JSON response indicating success and providing the
              endpoint information.
    """
    return json({"ok": True})


async def handle_websocket(request: Request, ws: Websocket):
    """
    Handle WebSocket connections and message exchanges.

    This function listens for incoming messages from the WebSocket
    client and echoes them back to the client.

    Args:
        request (Request): The Sanic request object containing the
                           request data.
        ws (Websocket): The WebSocket connection object used to
                        communicate with the client.

    Returns:
        None: This function runs indefinitely, processing messages
              until the connection is closed.
    """
    async for message in ws:
        await ws.send(message)


gateway.add_websocket_route(handle_websocket, '/')
