#!/usr/bin/env python

"""
Examples demonstrating language features for functions.

This is a "bikeshed" file containing a handful of examples/exercises that don't
fit well elsewhere.

See also functions.ipynb, scopes.ipynb, and scopes.py.

Most material on higher-order functions is in composers.py or decorators.py.

TODO: Either move these functions to other modules or better explain what this
      module should and shouldn't contain.
"""

import itertools
from decorators import peek_return

from fibonacci import fib


def make_counter(start=0):
    """
    Create and return a function that returns successive integers on each call.

    This implementation never assigns to a variable that already exists.
    """
    it = itertools.count(start)
    return lambda: next(it)


def make_counter_alt(start=0):
    """
    Create and return a function that returns successive integers on each call.

    This implementation does not involve iterators in any way.
    """
    def counter():
        nonlocal start
        current = start
        start += 1
        return current

    return counter


def make_next_fibonacci():
    """
    Create and return a function that returns successive Fibonacci numbers on
    each call.

    This implementation is simple, using an existing function in the project.
    """
    it = fib()
    return lambda: next(it)


def make_next_fibonacci_alt():
    """
    Create and return a function that returns successive Fibonacci numbers on
    each call.

    This implementation is self-contained: it does not use anything defined
    outside, not even builtins. It also does not involve iterators in any way.
    """
    a = 0
    b = 1

    def next_fib():
        nonlocal a, b
        ret = a
        a, b = b, a + b
        return ret

    return next_fib


def as_func(iterable):
    """
    Given an iterable, return a function that steps through it on each call.
    """
    it = iter(iterable)
    return lambda: next(it)


def as_iterator_limited(func, end_sentinel):
    """
    Given a parameterless function, return an iterator that calls it until
    end_sentinel is reached.
    """
    return iter(func, end_sentinel)


def as_iterator_limited_alt(func, end_sentinel):
    """
    Given a parameterless function, return an iterator that calls it until
    end_sentinel is reached.

    This is an alternative implementation of as_iterator_limited. One
    implementation uses the iter builtin; the other does not.
    """
    while True:
        result = func()
        if result == end_sentinel:
            return
        yield result


def as_iterator(func):
    """
    Given a parameterless function, return an iterator that repeatedly calls
    it.
    """
    return iter(func, object())


def as_iterator_alt(func):
    """
    Given a parameterless function, return an iterator that repeatedly calls
    it.

    This is an alternative implementation of as_iterator. One implementation
    uses the iter builtin; the other does not.
    """
    while True:
        yield func()


def count_tree_nodes(root):
    """
    Recursively count nodes in a tuple structure.

    Empty tuples and non-tuples are leaves. Other objects are internal nodes.
    The structure is treated as a tree: objects reached in more than one way
    are counted multiple times. No memoization is performed.

    This is a simple recursive implementation. No helper function is used.
    """
    if not isinstance(root, tuple):
        return 1

    return sum(count_tree_nodes(element) for element in root) + 1


def count_tree_nodes_alt(root):
    """
    Recursively count nodes in a tuple structure.

    Empty tuples and non-tuples are leaves. Other objects are internal nodes.
    The structure is treated as a tree: objects reached in more than one way
    are counted multiple times. No memoization is performed.

    This alternative implementation defines and calls a recursive helper
    function that does not return a value (really, it always returns None).
    No other callables, besides the helper and maybe builtins, are ever used.
    count_tree_nodes_alt never calls itself, nor does the helper ever call it.
    """
    count = 0

    def count_nodes(root):
        nonlocal count
        count +=1
        if not isinstance(root, tuple):
            return
        for element in root:
            count_nodes(element)

    count_nodes(root)
    return count


def count_tree_nodes_instrumented(root):
    """
    Call count_tree_nodes as if it were decorated with @decorators.peek_return.

    No logic from count_tree_nodes is reproduced. Subsequent calls to it do not
    have the modified behavior even if a prior call to it through this function
    raised an exception. But concurrent calls--like if it's called on another
    thread before a call to it through this function returns--need not be safe.

    Likewise, no logic from @peek_return is reproduced. If its behavior were to
    change--for example by using a different output format or even giving it by
    an entirely different means, such as posting it to a network server--then
    tests would need to change, but this function's implementation would not.
    """
    global count_tree_nodes
    non_decorated = count_tree_nodes
    count_tree_nodes = peek_return(count_tree_nodes)
    try:
        return count_tree_nodes(root)
    finally:
        count_tree_nodes = non_decorated


if __name__ == '__main__':
    import doctest
    doctest.testmod()
