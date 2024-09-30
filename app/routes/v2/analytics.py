from sanic import Blueprint, text

analytics = Blueprint('analytics', url_prefix='/analytics')


@analytics.get("/")
async def get_analytics(request):
    return text('analytics')
