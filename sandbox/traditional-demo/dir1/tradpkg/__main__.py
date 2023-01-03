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
