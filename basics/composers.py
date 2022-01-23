"""Function composition."""


def compose2(f, g):
    """
    Take two unary functions and returns their composition.

    >>> def square(x):
    ...     return x**2
    >>> fourth = compose2(square,square)
    >>> fourth(2)
    16
    >>> fourth(3)
    81
    >>> def inc(x):
    ...     return x + 1
    >>> squareplusone = compose2(inc,square)
    >>> squareplusone(2)
    5
    >>> squareplusone(10)
    101
    >>> compose2(square,inc)(2)
    9
    """
    return lambda x: f(g(x))


# Can also run:  python -m doctest composers.py
# (Pass -v after doctest for verbose output.)
if __name__ == '__main__':
    import doctest
    doctest.testmod()
