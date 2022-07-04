"""
Lucas sequences.

https://en.wikipedia.org/wiki/Generalizations_of_Fibonacci_numbers#Lucas_sequences

(Greedo shoots first.)
"""


def compute_lucas_u(p, q, n):
    """
    Compute element n of the (p, q) Lucas "U" sequence.

    This is the naive recursive algorithm, taking exponential time.

    p and q may be any integers. If n is negative, ValueError is raised.
    """