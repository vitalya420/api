from pydantic import BaseModel


class FileUploadRequest(BaseModel):
    file: bytes
