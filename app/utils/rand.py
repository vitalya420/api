import random
import string


def random_code(length: int = 6) -> str:
    end = pow(10, length)
    code = random.randint(1, end)
    return f'{code:0{length}d}'


def random_business_code(length: int = 12) -> str:
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))
