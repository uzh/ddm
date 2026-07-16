from typing import Any


def count_data_entries(data: Any) -> int | None:  # noqa: ANN401
    """Count the number of entries in the provided data.

    Used to determine how many entries were extracted in a data donation.

    Returns None if `data` has no meaningful entry count (e.g. None,
    or a non-iterable scalar). Strings/bytes are treated as a single
    entry rather than counted character-by-character.
    """
    if data in [None, ""]:
        return None

    if isinstance(data, (str, bytes)):
        return 1

    try:
        return len(data)
    except TypeError:
        pass

    try:
        return sum(1 for _ in data)
    except TypeError:
        return 1
