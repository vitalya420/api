from sanic import Blueprint, text
from sanic import Request

token = Blueprint('token', url_prefix='/token')


@token.post('/refresh')
async def refresh_token(request: Request):
    return text('refresh token')


@token.post('/revoke')
async def revoke_token(request: Request):
    return text('revoke')


@token.post('/revoke-all')
async def revoke_all_tokens(request: Request):
    return text('revoke all tokens')
