"""Function composition."""


def compose2(f, g):
    """
    Take two unary functions and return their composition.

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


def repeat_compose_recursive(function, count):
    """
    Compose the unary function, function, with itself count times.

    >>> def inc(x): return x + 1
    >>> repeat_compose_recursive(inc, 0)(1)
    1
    >>> repeat_compose_recursive(inc, 1)(1)
    2
    >>> repeat_compose_recursive(inc, 90)(1)
    91
    >>> repeat_compose_recursive(inc, 9000)(1)
    Traceback (most recent call last):
      ...
    RecursionError: maximum recursion depth exceeded in comparison
    """
    if count == 0: 
        return lambda x: x
    return compose2(function, repeat_compose_recursive(function, count - 1))


def repeat_compose_chained(function, count):
    """
    Compose the unary function, function, with itself count times.

    >>> def square(x):
    ...     return x**2
    >>> repeat_compose_chained(square, 0)(2)
    2
    >>> repeat_compose_chained(square, 1)(2)
    4
    >>> repeat_compose_chained(square, 2)(2)
    16
    >>> def inc(x): return x + 1
    >>> repeat_compose_chained(inc, 5000)(1)
    Traceback (most recent call last):
      ...
    RecursionError: maximum recursion depth exceeded
    """
    rvalue = lambda x: x
    for _ in range(count):
        rvalue = compose2(function, rvalue)
    return rvalue


def repeat_compose(function, count):
    """
    Compose the unary function, function, with itself count times.

    >>> def square(x):
    ...     return x**2
    >>> repeat_compose(square, 0)(2)
    2
    >>> repeat_compose(square, 1)(2)
    4
    >>> repeat_compose(square, 2)(2)
    16
    >>> def inc(x): return x + 1
    >>> repeat_compose(inc, 5000)(1)
    5001
    """
    def rvalue(x):
        for _ in range(count):
            x = function(x)
        return x
    return rvalue


# Can also run:  python -m doctest composers.py
# (Pass -v after doctest for verbose output.)
if __name__ == '__main__':
    import doctest
    doctest.testmod()
