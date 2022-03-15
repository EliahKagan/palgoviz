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
    return 42


def is_sorted(items):
    """Check if an iterable is sorted."""
    my_items = list(items)
    return my_items == sorted(my_items)


def alert(message):
    """Print an alert to standard error, with a simple "alert:" prefix."""
    print(f'alert: {message}', file=sys.stderr)
