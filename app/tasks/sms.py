import asyncio
from typing import Optional

from app.utils.rand import random_code


async def send_sms_to_phone(
    phone: str, code: Optional[str] = None, code_length: Optional[int] = None
):
    code = code or random_code(code_length or 6)
    print(f"Sending some sms to phone with code {code}")
