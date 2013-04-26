from werkzeug.security import safe_str_cmp


def multi_constant_time_compare(value, expecteds):
    """
    Compares ``value`` against each of the strings in ``expecteds``, returns
    ``True`` if it is equal to any of them, and ``False`` otherwise.

    The amount of time this takes to execute is independent of how similar
    ``value`` is to the items in ``expecteds``.
    """
    found = 0
    for expected in expecteds:
        found |= safe_str_cmp(value, expected)
    return bool(found)
