import asyncio

from sanic import Blueprint, ServiceUnavailable, BadRequest
from sanic.request import Request
from sanic.response import json
from sanic_ext import validate

from app.exceptions import InvalidPhoneNumber
from app.schemas import User, UserCreate
from app.schemas.user import UserCodeConfirm
from app.security import rules
from app.security import (login_required,
                          business_id_required,
                          otp_context_required)
from app.security import validator
from app.tasks import send_sms_to_phone

user = Blueprint('user', url_prefix='/user')


@user.get('/')
# @rules(login_required, business_id_required)
async def get_user(request: Request):
    validator.validate_phone_number("+3813", raise_exception=True)
    ret = await request.app.ctx.services.user.create(first_name='Hello', last_name="World", phone='+381048')
    return json(User.model_validate(ret, from_attributes=True).model_dump())


@user.post('/')
@rules(business_id_required)
@validate(UserCreate)
async def create_user(request: Request, body: UserCreate):
    if not validator.validate_ukrainian_phone_number(body.phone):
        raise InvalidPhoneNumber(context={"errors": {"phone": "Invalid phone number"}})
    try:
        auth_service = request.app.ctx.services.auth
        await asyncio.wait_for(auth_service.send_otp(body.phone), timeout=5)
        return json({"message": f"SMS with one time code sent to {body.phone}"})
    except asyncio.TimeoutError:
        raise ServiceUnavailable("Sorry, we have some troubles to send one time code to you. Try again later.")


@user.post('/confirm')
@validate(UserCodeConfirm)
@rules(otp_context_required, business_id_required)
async def code_confirm(request: Request, body: UserCodeConfirm):
    real_code = request.ctx.otp.code
    if body.otp == real_code:
        auth_service = request.app.ctx.services.auth
        await auth_service.set_code_used(request.ctx.otp.id)
        return json({"message": "OTP code is valid!"})
    raise BadRequest("Invalid OTP code.")


@user.put('/')
@rules(login_required, business_id_required)
async def update_user(request: Request):
    pass


@user.delete('/')
@rules(login_required, business_id_required)
async def delete_user(request: Request):
    pass
