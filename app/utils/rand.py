import random


def random_code(length: int = 6) -> str:
    end = pow(10, length)
    code = random.randint(1, end)
    return f'{code:0{length}d}'
