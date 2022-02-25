#!/usr/bin/env python

"""
More generators and comprehensions.

See also gencomp1.py.
"""

import itertools


def three_sums(a, b, c):
    """
    Make a set of all sums x + y + z. Take x, y, z from a, b, c, respectively.

    a, b, and c may be any iterables whose elements are numbers.

    >>> three_sums([2, 3], [], [20, 30])
    set()
    >>> a = (n * 10 for n in (1, 2, 3))
    >>> b = [7, 7, 14]
    >>> c = iter(range(2, 5))
    >>> s = three_sums(a, b, c)
    >>> isinstance(s, set)
    True
    >>> sorted(s)
    [19, 20, 21, 26, 27, 28, 29, 30, 31, 36, 37, 38, 39, 40, 41, 46, 47, 48]
    >>> three_sums(range(10), range(10), range(10)) == set(range(28))
    True
    """
    return {sum(v) for v in itertools.product(a, b, c)}


def three_sums_alt(a, b, c):
    """
    Make a set of all sums x + y + z. Take x, y, z from a, b, c, respectively.

    a, b, and c may be any iterables whose elements are numbers.

    This alternative implementation differs from the above implementation. One
    of these implementations uses something from itertools. The other does not.

    >>> three_sums_alt([2, 3], [], [20, 30])
    set()
    >>> a = (n * 10 for n in (1, 2, 3))
    >>> b = [7, 7, 14]
    >>> c = iter(range(2, 5))
    >>> s = three_sums_alt(a, b, c)
    >>> isinstance(s, set)
    True
    >>> sorted(s)
    [19, 20, 21, 26, 27, 28, 29, 30, 31, 36, 37, 38, 39, 40, 41, 46, 47, 48]
    >>> three_sums_alt(range(10), range(10), range(10)) == set(range(28))
    True
    """
    xs = list(a)
    ys = list(b)
    zs = list(c)
    return {x + y + z for x in xs for y in ys for z in zs}


def three_sum_indices_1(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers.

    This is the first of four implementations. Two of these implementations
    return generator expressions and do not contain loops. The other two are
    written as generator functions and do not use comprehensions.

    FIXME: Add tests.
    """
    return ((i, j, k) for (i, x), (j, y), (k, z)
            in itertools.product(enumerate(a), enumerate(b), enumerate(c))
            if x != y != z != x and x + y + z == target)


def three_sum_indices_2(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers.

    This is the second of four implementations.

    FIXME: Add tests.
    """
    triples = itertools.product(enumerate(a), enumerate(b), enumerate(c))

    for (i, x), (j, y), (k, z) in triples:
        if x != y and y != z and z != x and x + y + z == target:
            yield i, j, k


def three_sum_indices_alt_3(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers.

    This is the third of four implementations.

    [FIXME: Remove this para. Maybe commit it first -- it may be useful later.]
    This behaves the same as three_sum_indices (above) but is implemented
    differently. One of these implementations consists of a single return
    statement (that is nonetheless easy to understand) or it could be trivially
    modified to put it in that form. The other does not rely on any imports.

    FIXME: Add tests.
    """
    xs = list(a)
    ys = list(b)
    zs = list(c)

    return ((i, j, k)
            for i, x in enumerate(xs)
            for j, y in enumerate(ys) if x != y
            for k, z in enumerate(zs)
            if x != z and y != z and x + y + z == target)


def three_sum_indices_alt_4(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers.

    This is the fourth of four implementations.
    """
    xs = list(a)
    ys = list(b)
    zs = list(c)

    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if x == y:
                continue
            for k, z in enumerate(zs):
                if x != z and y != z and x + y + z == target:
                    yield i, j, k
