#!/usr/bin/env python

# Copyright (c) 2022 David Vassallo and Eliah Kagan
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""
Command-line program that prints the first N Fibonacci numbers, where N is
passed as its sole command-line argument.

Usage:

    fib.py {N}

Example:

    > python palgoviz/fib.py 10
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34.

For other Fibonacci code, see fibonacci.py, which defines the fib_n function
this script uses. See also the visualizations in subproblems.ipynb.
"""

import sys

from palgoviz.fibonacci import fib_n


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


# Although I sometimes prefer to call this function "run" (since it is not a
# true entry point in the sense that it is in C and C++), it is more commonly
# called called "main", which I do here for demonstration purposes.  -Eliah
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
