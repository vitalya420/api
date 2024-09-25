from urllib.request import Request

from sanic import Sanic, text

app = Sanic(__name__)


@app.route('/')
def index(request: Request):
    return text("Hello World!")

