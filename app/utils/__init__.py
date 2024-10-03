def force_id(object_):
    if isinstance(object_, int):
        return object_
    return object_.id


def force_business_code(object_):
    if isinstance(object_, str):
        return object_
    return object_.code
