"""Some simple functions, for unit testing."""


def answer():
    """
    Return the int said to answer the question of life/the universe/everything.
    """
    return 42  # return 43  # FIXME: Should be 42.


def is_sorted(items):
    """Check if an iterable is sorted."""
    values = list(items)
    return values == sorted(values)
