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
