import re

pattern = re.compile(r'\+?(\d{1,3})\s*(\d{1,4})\s*(\d{1,4})\s*(\d{1,4})\s*(\d{1,4})?', re.VERBOSE)


def normalize_phone_number(phone):
    match = pattern.search(phone)
    if match:
        country_code = match.group(1)
        area_code = match.group(2) or ''
        first_part = match.group(3)
        second_part = match.group(4)
        third_part = match.group(5) or ''

        normalized = f"+{country_code}{area_code}{first_part}{second_part}"

        if third_part:
            normalized += f"{third_part}"

        return normalized.strip()
    else:
        return None
