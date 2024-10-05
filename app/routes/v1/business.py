from sanic import Blueprint, Request

from app.security import rules, login_required
from app.security.decorators import admin_access

business = Blueprint('business', url_prefix='/business')


@business.get('/<business_id>')
async def get_business(request: Request):
    pass


@business.post('/')
@rules(login_required, admin_access)
async def create_business(request: Request):
    pass


@business.patch('/<business_id>')
async def update_business(request: Request):
    pass
