#!/usr/bin/env python

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

"""Function composition."""

__all__ = [
    'compose2',
    'repeat_compose_recursive',
    'repeat_compose_chained',
    'repeat_compose',
    'compose',
    'curry_one',
]

from palgoviz.util import identity_function


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

    Should fail with "...depth exceeded" or "...depth exceeded in comparison":

    >>> repeat_compose_recursive(inc, 9000)(1)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    RecursionError: maximum recursion depth exceeded...
    """
    if count == 0:
        return identity_function
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
    rvalue = identity_function
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

    All functions passed to compose are assumed to be unary.

    >>> compose()(3)
    3
    >>> def fa(x): return x + 'a'
    >>> def fb(x): return x + 'b'
    >>> def fc(x): return x + 'c'
    >>> def fd(x): return x + 'd'
    >>> def fe(x): return x + 'e'
    >>> compose(fa, fb, fc, fd, fe)('z')
    'zedcba'
    >>> from palgoviz.adders import make_adder
    >>> add_50005000 = compose(*(make_adder(i) for i in range(1, 10_001)))
    >>> add_50005000(7)
    50005007
    """
    def rvalue(x):
        for function in reversed(functions):
            x = function(x)
        return x

    return rvalue


def curry_one(function):
    """
    Convert a binary function to a unary function returning a unary function.

    Calling the returned function binds a first argument, thus returning a
    unary function requiring only a second argument. After g = curry(f), both
    f(x, y) and g(x)(y) have the same behavior and results.

    >>> import operator
    >>> curry_one(operator.add)('ab')('cd')
    'abcd'
    >>> curry_one(compose)(lambda x: x + 'a')(lambda x: x + 'b')('z')
    'zba'
    """
    return lambda x: lambda y: function(x, y)


# TODO: Eventually cover other forms of currying, the difference between
#       currying and partial function application, and functools.partial.


# Can also run:  python -m doctest palgoviz/composers.py
# (Pass "-v" after "doctest" for verbose output.)
if __name__ == '__main__':
    import doctest
    doctest.testmod()
