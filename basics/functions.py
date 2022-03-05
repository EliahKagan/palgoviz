#!/usr/bin/env python

"""
Examples demonstrating language features for functions.

This is a "bikeshed" file containing a handful of examples/exercises that don't
fit well elsewhere.

See also functions.ipynb, scopes.ipynb, and scopes.py.

Most material on higher-order functions is in composers.py or decorators.py.

TODO: Either move these functions to other modules or better explain what the
module should and shouldn't contain.
"""


def make_counter(start=0):
    """
    Create and return a function that returns successive integers on each call.

    This implementation never assigns to a variable that already exists.

    >>> f = make_counter()
    >>> [f(), f()]
    [0, 1]
    >>> g = make_counter()
    >>> [f(), g(), f(), g(), g()]
    [2, 0, 3, 1, 2]
    >>> h = make_counter(10)
    >>> [h(), f(), g(), h(), g(), h(), h(), g(), g(), f(), h()]
    [10, 4, 3, 11, 4, 12, 13, 5, 6, 5, 14]
    """
    ...  # FIXME: Implement this.


def make_counter_alt(start=0):
    """
    Create and return a function that returns successive integers on each call.

    This implementation does not involve iterators in any way.

    >>> f = make_counter_alt()
    >>> [f(), f()]
    [0, 1]
    >>> g = make_counter_alt()
    >>> [f(), g(), f(), g(), g()]
    [2, 0, 3, 1, 2]
    >>> h = make_counter_alt(10)
    >>> [h(), f(), g(), h(), g(), h(), h(), g(), g(), f(), h()]
    [10, 4, 3, 11, 4, 12, 13, 5, 6, 5, 14]
    """
    ...  # FIXME: Implement this.


def make_next_fibonacci():
    """
    Create and return a function that returns successive Fibonacci numbers on
    each call.

    This implementation is simple, using an existing function in the project.

    >>> f = make_next_fibonacci()
    >>> [f() for _ in range(5)]
    [0, 1, 1, 2, 3]
    >>> g = make_next_fibonacci()
    >>> [x for _ in range(5) for x in (g(), f())]
    [0, 5, 1, 8, 1, 13, 2, 21, 3, 34]
    >>> [f(), f(), g()]
    [55, 89, 5]
    """
    ...  # FIXME: Implement this.


def make_next_fibonacci_alt():
    """
    Create and return a function that returns successive Fibonacci numbers on
    each call.

    This implementation is self-contained: it does not use anything defined
    outside, not even builtins. It also does not involve iterators in any way.

    >>> f = make_next_fibonacci_alt()
    >>> [f() for _ in range(5)]
    [0, 1, 1, 2, 3]
    >>> g = make_next_fibonacci_alt()
    >>> [x for _ in range(5) for x in (g(), f())]
    [0, 5, 1, 8, 1, 13, 2, 21, 3, 34]
    >>> [f(), f(), g()]
    [55, 89, 5]
    """
    ...  # FIXME: Implement this.


if __name__ == '__main__':
    import doctest
    doctest.testmod()
