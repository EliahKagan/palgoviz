"""2-dimensional grids, represented as lists of lists of numbers."""


def make_grid(m, n):
    """
    Make a grid of zeros of height m and width n.

    A list of m lists of n 0s is returned.

    Time complexity is O(mn).
    """
    return [[0] * n for _ in range(m)]