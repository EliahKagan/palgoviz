#!/usr/bin/env python

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


def compose(*functions):
    """
    Compose functions left to right, so the rightmost function is called first.

    This supports being called with a large number of arguments.

    >>> compose()(3)
    3
    >>> def fa(x): return x + 'a'
    >>> def fb(x): return x + 'b'
    >>> def fc(x): return x + 'c'
    >>> def fd(x): return x + 'd'
    >>> def fe(x): return x + 'e'
    >>> compose(fa, fb, fc, fd, fe)('z')
    'zedcba'
    >>> from adders import make_adder
    >>> add_50005000 = compose(*(make_adder(i) for i in range(1, 10_001)))
    >>> add_50005000(7)
    50005007
    """
    # FIXME: Implement this.


def curry_one(function):
    """
    Convert a binary function to a unary function returning a unary function.

    Calling the returned function binds a first argument, thus returning a
    unary function requiring only a second argument. That is, if curry(f)
    returns g, both f(x, y) and g(x)(y) have the same behavior and results.

    >>> import operator
    >>> curry_one(operator.add)('ab')('cd')
    'abcd'
    >>> curry_one(compose)(lambda x: x + 'a')(lambda x: x + 'b')('z')
    'zba'
    """
    # FIXME: Implement this.


# TODO: Eventually cover other forms of currying, the difference between
#       currying and partial function application, and functools.partial.


__all__ = [thing.__name__ for thing in (
    compose2,
    repeat_compose_recursive,
    repeat_compose_chained,
    repeat_compose,
    compose,
    curry_one,
)]


# Can also run:  python -m doctest composers.py
# (Pass -v after doctest for verbose output.)
if __name__ == '__main__':
    import doctest
    doctest.testmod()
