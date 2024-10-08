import bcrypt


def hash_password(plain_password: str):
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
