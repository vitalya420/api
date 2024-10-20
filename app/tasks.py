import asyncio
import io
from typing import Optional

from PIL import Image

from app.utils import random_code


async def send_sms_to_phone(
    phone: str, code: Optional[str] = None, code_length: Optional[int] = None
):
    """
    Send an SMS to a specified phone number with a verification code.

    This asynchronous function sends an SMS message to the provided phone number.
    If a verification code is not provided, a random code will be generated using
    the specified length. The default length for the generated code is 6 digits.

    Args:
        phone (str): The phone number to which the SMS will be sent.
                     It should be in a valid format.
        code (Optional[str]): An optional verification code to send.
                              If not provided, a random code will be generated.
        code_length (Optional[int]): An optional length for the generated code.
                                      If not provided, the default length of 6 will be used.

    Returns:
        None: This function does not return a value. It performs an action (sending an SMS).

    Example:
        >>> await send_sms_to_phone("+1234567890")
        Sending some sms to phone with code 123456  # Example output, actual output will vary

        >>> await send_sms_to_phone("+1234567890", code="ABC123")
        Sending some sms to phone with code ABC123
    """
    code = code or random_code(code_length or 6)
    print(f"Sending some sms to phone with code {code}")


async def compress_image(image_bytes: bytes, quality: int = 70):
    def _do_compress():
        image_file = io.BytesIO(image_bytes)
        image = Image.open(image_file)

        if image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        ):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        return buffer.getvalue()

    return await asyncio.get_event_loop().run_in_executor(None, _do_compress)
