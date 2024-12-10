import random
import string


def create_asciidigits_id(n_chars: int) -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(n_chars))
