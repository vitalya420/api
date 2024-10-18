import os.path
from hashlib import md5

import aiofiles
from PIL import UnidentifiedImageError
from sanic import Blueprint, Request, json, BadRequest
from sanic.request import File
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi

from app.decorators import login_required
from app.schemas import FileUploadRequest
from app.tasks import compress_image

file_upload = Blueprint('file_upload', url_prefix='/upload')


@file_upload.post('/')
@openapi.definition(
    body={"multipart/form-data": FileUploadRequest.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )},
    secured={"token": []}
)
@login_required
async def handle_file_upload(request: Request, ):
    try:
        file_content: File = request.files['file'][0]
        compressed = await compress_image(file_content.body)
        new_file_name = f'{md5(file_content.body).hexdigest()}.jpg'
        path = os.path.join(request.app.ctx.user_uploads_dir, new_file_name)
        async with aiofiles.open(path, 'wb') as f:
            await f.write(compressed)
        endpoint = os.path.join(request.app.ctx.user_uploads_endpoint, new_file_name)
        return json({"success": True, "url": endpoint})
    except (KeyError, UnidentifiedImageError):
        raise BadRequest
