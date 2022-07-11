"""
Print a grid.

This demonstrates running the top-level package as a script.

Usage example:

    python -m tradpkg 3 5
"""

import pprint
import sys

from .subpkg.grids import make_grid


def run():  # We usually call this main(), but it can be called anything.
    match sys.argv:
        case [_]:
            m = 5
            n = 7
        case [_, arg1, arg2]:
            m = int(arg1)
            n = int(arg2)

    pprint.pprint(make_grid(m, n), width=40)


if __name__ == '__main__':
    run()
