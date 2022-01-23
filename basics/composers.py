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


def repeat_compose(function, count):
    """
    Composes the unary function, function, with itself count times.
    >>> def square(x):
    ...     return x**2
    >>> repeat_compose(square, 0)(2)
    2
    >>> repeat_compose(square, 1)(2)
    4
    >>> repeat_compose(square, 2)(2)
    16
    """
    rvalue = lambda x: x
    for i in range(count):
        rvalue_tmp = rvalue  # But this is also scoped to repeat_compose.

        # This produces the same (bad) behavior as the assignment below
        def rvalue(x):
            return function(rvalue(x))

        # This has infinite recursion.
        rvalue = lambda x: function(rvalue(x))
    return rvalue


# Can also run:  python -m doctest composers.py
# (Pass -v after doctest for verbose output.)
if __name__ == '__main__':
    import doctest
    doctest.testmod()
