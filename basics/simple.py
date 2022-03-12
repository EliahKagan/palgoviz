"""Some simple functions, for unit testing."""

import sys


def answer():
    """
    Return the int said to answer the question of life/the universe/everything.
    """
    return 42  # return 43  # FIXME: Should be 42.


def parse_yes_no(text):
    """Case-insensitively parse "yes" as True and "no" as False."""
    match text.lower():
        case 'yes':
            return True
        case 'no':
            return False
        case _:
            raise ValueError('text must be "yes" or "no" (or case variants)')


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
