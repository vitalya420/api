import os
from hashlib import md5

import aiofiles
from sanic.request import File

from app.request import ApiRequest
from app.tasks import compress_image

static_folder_path = os.path.join(os.getcwd(), "static")
user_uploads_folder = os.path.join(static_folder_path, "user_uploads")


async def save_image_from_request(
    request: ApiRequest,
):
    file_content: File = request.files["file"][0]
    compressed = await compress_image(file_content.body)
    new_file_name = f"{md5(file_content.body).hexdigest()}.jpg"
    path = os.path.join(user_uploads_folder, new_file_name)
    async with aiofiles.open(path, "wb") as f:
        await f.write(compressed)
    endpoint = os.path.join(request.app.ctx.user_uploads_endpoint, new_file_name)
    return endpoint
