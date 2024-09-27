from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from app.schemas import User
from app.security import rules
from app.security import (login_required,
                          business_id_required)
from app.security import validator

user = Blueprint('user', url_prefix='/user')


@user.get('/')
# @rules(login_required, business_id_required)
async def get_user(request: Request):
    validator.validate_phone_number("+3813", raise_exception=True)
    ret = await request.app.ctx.services.user.create(first_name='Hello', last_name="World", phone='+381048')
    return json(User.model_validate(ret, from_attributes=True).model_dump())


@user.post('/')
@rules(login_required, business_id_required)
async def create_user(request: Request):
    pass


@user.put('/')
@rules(login_required, business_id_required)
async def update_user(request: Request):
    pass


@user.delete('/')
@rules(login_required, business_id_required)
async def delete_user(request: Request):
    pass
