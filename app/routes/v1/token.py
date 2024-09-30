from sanic import Blueprint, text
from sanic import Request
from sanic_ext import validate

from app.schemas.tokens import RefreshTokenRequest
from app.security import rules, login_required
from app.services import tokens

token = Blueprint('token', url_prefix='/token')


@token.post('/refresh')
@validate(json=RefreshTokenRequest)
async def refresh_token(request: Request, body: RefreshTokenRequest):
    await tokens.issue_new_tokens(body.refresh_token)
    return text('refresh token')


@token.post('/<jti>/revoke')
@rules(login_required)
async def revoke_token(request: Request):
    return text('revoke')


@token.post('/revoke-all')
async def revoke_all_tokens(request: Request):
    return text('revoke all tokens')
