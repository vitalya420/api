from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from app.schemas import User

user = Blueprint('user', url_prefix='/user')


@user.get('/')
async def get_user(request: Request):
    ret = await request.app.ctx.services.user.create(first_name='Hello', last_name="World", phone='+381048')
    return json(User.model_validate(ret, from_attributes=True).model_dump())
