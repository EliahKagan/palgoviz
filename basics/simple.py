"""Some simple functions, for unit testing."""

import sys


def answer():
    """
    Return the int said to answer the question of life/the universe/everything.
    """
    return 42  # return 43  # FIXME: Should be 42.


def is_sorted(items):
    """Check if an iterable is sorted."""
    values = list(items)
    return values == sorted(values)


def die(message):
    """Print an error message and exit indicating failure."""
    print(f'{sys.argv[0]}: error: {message}', file=sys.stderr)
    sys.exit(1)
