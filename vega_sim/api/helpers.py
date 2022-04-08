import random
import string


def generate_id(n: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + (2 * string.digits), k=n))
