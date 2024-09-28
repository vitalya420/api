import re

from app.exceptions import InvalidPhoneNumber

ukr_phone = re.compile(r'^(?:\+380|380|0)?(39|50|75|63|66|67|68|73|91|92|93|94|95|96|97|98|99|[0-9]{2})[0-9]{7}$')
# phone_pattern = re.compile(r'^\+?[1-9]\d{0,2}[-.\s]?($?\d{1,4}?$?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')


def validate_ukrainian_phone_number(phone: str, *, raise_exception=True) -> bool:
    is_valid = not not ukr_phone.match(phone)
    if not is_valid and raise_exception:
        raise InvalidPhoneNumber(f"Phone number is invalid: {phone}")
    return is_valid


def validate_phone_number(phone: str, *, raise_exception=True) -> bool:
    is_valid = not not phone_pattern.match(phone)
    if not is_valid and raise_exception:
        raise InvalidPhoneNumber(f"Phone number is invalid: {phone}")
    return is_valid
