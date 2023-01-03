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
Lucas sequences.

https://en.wikipedia.org/wiki/Generalizations_of_Fibonacci_numbers#Lucas_sequences

(Han and Greedo shoot at the same time.)
"""


def compute_lucas_u(p, q, n):
    """
    Compute element n of the (p, q) Lucas "U" sequence.

    This is the naive recursive algorithm, taking exponential time.

    p and q may be any integers. If n is negative, ValueError is raised.
    """
    if n < 0:
        raise ValueError('n must not be negative')

    if n == 0:
        return 0

    if n == 1:
        return 1

    return p*compute_lucas_u(p, q, n - 1) - q*compute_lucas_u(p, q, n - 2)
