#!/usr/bin/env python

"""
Command-line program that prints the first N Fibonacci numbers, where N is
passed as its sole command-line argument.

Usage:

    fib {N}

Example:

    > python fib.py 10
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34.
"""

import sys

from generators_and_comprehensions import fib_n


def _show_message(prefix, message):
    """Display a message to standard error. Helper for _warn() and _die()."""
    print(f'{sys.argv[0]}: {prefix}: {message}', file=sys.stderr)


def _warn(message):
    """Print a warning message to standard error."""
    _show_message('warning', message)


def _die(message):
    """Print an error message to standard error. Exit with failure status."""
    _show_message('error', message)
    sys.exit(1)


# Although I tend to prefer calling this function "run" (since it is not a true
# entry point in the sense that it is in C and C++), it is more commonly called
# called "main", which I do here for demonstration purposes.
def main():
    """Run the script, printing Fibonacci numbers or printing an error."""
    if len(sys.argv) < 2:
        _die('too few arguments')
    if len(sys.argv) > 2:
        _die('too many arguments')

    try:
        n = int(sys.argv[1])
    except ValueError as e: 
        _die(e)

    try:
        result = fib_n(n)
    except ValueError as e: 
        _die(e)

    if n == 0:
        _warn('printing ZERO numbers, as requested')

    print(*result, sep=', ', end='.\n')


if __name__ == '__main__':
    main()
