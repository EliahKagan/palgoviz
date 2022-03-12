"""Some simple code, for unit testing."""

import sys


MY_NONE = None


class Widget:
    """Something with size and color attributes, disallowing new attributes."""

    __slots__ = ('size', 'color')

    def __init__(self, size, color):
        """Create a new widget of the specified size and color."""
        self.size = size
        self.color = color


def answer():
    """
    Return the int said to answer the question of life/the universe/everything.
    """
    return 42  # return 43  # FIXME: Should be 42.


def is_sorted(items):
    """Check if an iterable is sorted."""
    values = list(items)
    return values == sorted(values)


def alert(message):
    """Print an alert to standard error, with a simple "alert:" prefix."""
    print('alert:', message, file=sys.stderr)


def bail_if(condition):
    """Exit indicating failure if the condition evaluates as true."""
    if condition:
        sys.exit(1)
