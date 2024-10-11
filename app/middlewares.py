from sanic import Request, HTTPResponse

from app.config import config


async def request_basic_auth(request: Request):
    pass


async def set_cors_headers(request: Request, response: HTTPResponse):
    response.headers["Access-Control-Allow-Origin"] = "*"
