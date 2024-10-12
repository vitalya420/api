import random
import re
import string
from functools import wraps
from typing import Protocol, Union, Callable

from sanic import json


class _HasID(Protocol):
    id: int


class _HasCode(Protocol):
    code: str


def force_id(object_: Union[int, _HasID]) -> int:
    """
    Retrieve the ID from the given object or return the integer if it is already an ID.

    Args:
        object_ (Union[int, HasID]): The object from which to retrieve the ID.
                                      It can be an integer or an object that implements the HasID protocol.

    Returns:
        int: The ID of the object.

    Raises:
        AttributeError: If object_ is not an int and does not have an id attribute.
    """
    if isinstance(object_, int):
        return object_
    return object_.id


def force_code(object_: Union[str, _HasCode]) -> str:
    """
    Retrieve the code from the given object or return the string if it is already a code.

    This function checks if the provided object is a string. If it is, the function returns
    the string directly. If the object is not a string, it is expected to conform to the
    _HasCode protocol, which requires a 'code' attribute of type str. The function then
    returns the value of that 'code' attribute.

    Args:
        object_ (Union[str, _HasCode]): The object from which to retrieve the code.
                                         It can be a string or an object that implements
                                         the _HasCode protocol.

    Returns:
        str: The code of the object.

    Raises:
        AttributeError: If object_ is not a string and does not have a 'code' attribute.
    """
    if isinstance(object_, str):
        return object_
    return object_.code


internation_phone_pattern = re.compile(
    r"\+?(\d{1,3})\s*(\d{1,4})\s*(\d{1,4})\s*(\d{1,4})\s*(\d{1,4})?", re.VERBOSE
)


def normalize_phone_number(phone: str):
    """
    Normalize a given phone number into an international format.

    This function takes a phone number as a string and attempts to match it
    against a predefined international phone number pattern. If a match is found,
    it extracts the country code, area code, and the main parts of the phone number,
    and then formats them into a standardized international format.

    The resulting format will be:
    +<country_code><area_code><first_part><second_part><third_part>

    Args:
        phone (str): The phone number to normalize, which can include various formats
                     and optional whitespace.

    Returns:
        str: The normalized phone number in international format, or None if the
             input does not match the expected pattern.

    Example:
        >>> normalize_phone_number("+1 800 555 1234")
        '+18005551234'

        >>> normalize_phone_number("800 555 1234")
        '+8005551234'

        >>> normalize_phone_number("invalid phone number")
        None
    """
    match = internation_phone_pattern.search(phone)
    if match:
        country_code = match.group(1)
        area_code = match.group(2) or ""
        first_part = match.group(3)
        second_part = match.group(4)
        third_part = match.group(5) or ""

        normalized = f"+{country_code}{area_code}{first_part}{second_part}"

        if third_part:
            normalized += f"{third_part}"

        return normalized.strip()
    else:
        return None


def random_code(length: int = 6) -> str:
    """
    Generate a random numeric code of a specified length.

    This function generates a random integer code with the specified number of digits.
    If the generated code has fewer digits than the specified length, it will be
    zero-padded to ensure it has the correct length.

    Args:
        length (int): The length of the code to generate. Default is 6.

    Returns:
        str: A string representation of the randomly generated numeric code,
             zero-padded to the specified length.

    Example:
        random_code(4)
        '0234'  # Example output, actual output will vary
    """
    end = pow(10, length)
    code = random.randint(1, end)
    return f"{code:0{length}d}"


def random_string_code(length: int = 12) -> str:
    """
    Generate a random string code consisting of uppercase letters.

    This function generates a random string of uppercase letters with the specified
    length. It is useful for creating unique identifiers for businesses or products.

    Args:
        length (int): The length of the business code to generate. Default is 12.

    Returns:
        str: A string of randomly selected uppercase letters of the specified length.

    Example:
        random_string_code(5)
        'ABCDE'  # Example output, actual output will vary
    """
    return "".join(random.choice(string.ascii_uppercase) for _ in range(length))
