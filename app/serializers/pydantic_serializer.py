from pydantic import BaseModel
from sanic import json


def serialize_pydantic(body: BaseModel, status: int):
    return json(body.model_dump(), status=status)
