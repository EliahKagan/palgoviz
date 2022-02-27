#!/usr/bin/env python

"""
More generators and comprehensions.

See also gencomp1.py and fibonacci.py.

Some, but not all, of the exercises in this file benefit from writing
comprehensions with multiple "for" (and sometimes multiple "if") clauses.
"""

from collections.abc import Iterable
import itertools


def product_two(a, b):
    """
    Like itertools.product, but must be called with exactly two iterables.

    This implementation returns a generator expression.

    >>> list(product_two('hi', 'bye'))
    [('h', 'b'), ('h', 'y'), ('h', 'e'), ('i', 'b'), ('i', 'y'), ('i', 'e')]
    >>> list(product_two(range(0), range(2)))
    []
    >>> list(product_two(range(2), range(0)))
    []
    >>> it = product_two((x - 1 for x in (1, 2)), (x + 5 for x in (3, 4)))
    >>> next(it)
    (0, 8)
    >>> list(it)
    [(0, 9), (1, 8), (1, 9)]
    """
    xs = list(a)
    ys = list(b)
    return ((x, y) for x in xs for y in ys)


def product_two_alt(a, b):
    """
    Like itertools.product, but must be called with exactly two iterables.

    This is like product_two above, but implemented as a generator function.

    >>> list(product_two_alt('hi', 'bye'))
    [('h', 'b'), ('h', 'y'), ('h', 'e'), ('i', 'b'), ('i', 'y'), ('i', 'e')]
    >>> list(product_two_alt(range(0), range(2)))
    []
    >>> list(product_two_alt(range(2), range(0)))
    []
    >>> it = product_two_alt((x - 1 for x in (1, 2)), (x + 5 for x in (3, 4)))
    >>> next(it)
    (0, 8)
    >>> list(it)
    [(0, 9), (1, 8), (1, 9)]
    """
    xs = list(a)
    ys = list(b)
    for x in xs:
        for y in ys:
            yield x, y


def ascending_countdowns():
    """
    Yield integers counting down to 0 from 0, then from 1, them from 2, etc.

    This implementation returns a generator expression.

    >>> from itertools import islice
    >>> list(islice(ascending_countdowns(), 25))
    [0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 6, 5, 4, 3]
    >>> sum(islice(ascending_countdowns(), 1_000_000))
    471108945
    """
    return (j for i in itertools.count() for j in range(i, -1, -1))


def ascending_countdowns_alt():
    """
    Yield integers counting down to 0 from 0, then from 1, them from 2, etc.

    This is like ascending_countdowns above, but implemented as a generator
    function.

    >>> from itertools import islice
    >>> list(islice(ascending_countdowns_alt(), 25))
    [0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 6, 5, 4, 3]
    >>> sum(islice(ascending_countdowns_alt(), 1_000_000))
    471108945
    """
    for i in itertools.count():
        yield from range(i, -1, -1)


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
    whose elements are numbers. The tuples are yielded in lexicographic order.

    This is the first of four implementations, which cover all four
    combinations of two independent choices:

        (A) Two implementations return generator expressions and do not contain
            loops. The other two are written as generator functions and do not
            use comprehensions.

        (B) Two implementations use something from itertools to simplify and
            shorten their code, but are slower in some situations (though the
            worst case efficiency is the same). The other two don't do that,
            instead avoiding doing extra work.

    It is acceptable for all four implementations to take time proportional to
    the product of the lengths of a, b, and c, even on average.

    >>> list(three_sum_indices_1([1, 2, 3], [10, 9], [7, 9, 8], 20))
    [(0, 0, 1), (1, 0, 2), (2, 0, 0), (2, 1, 2)]
    >>> next(three_sum_indices_1([0] * 10, [0] * 20, [0] * 30, 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> from itertools import repeat as r
    >>> sum(1 for _ in three_sum_indices_1(r(1, 10), r(2, 20), r(3, 30), 6))
    6000
    """
    return ((i, j, k) for (i, x), (j, y), (k, z)
            in itertools.product(enumerate(a), enumerate(b), enumerate(c))
            if x != y != z != x and x + y + z == target)


def three_sum_indices_2(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers. The tuples are yielded in lexicographic order.

    This is the second of four implementations.

    >>> list(three_sum_indices_2([1, 2, 3], [10, 9], [7, 9, 8], 20))
    [(0, 0, 1), (1, 0, 2), (2, 0, 0), (2, 1, 2)]
    >>> next(three_sum_indices_2([0] * 10, [0] * 20, [0] * 30, 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> from itertools import repeat as r
    >>> sum(1 for _ in three_sum_indices_2(r(1, 10), r(2, 20), r(3, 30), 6))
    6000
    """
    triples = itertools.product(enumerate(a), enumerate(b), enumerate(c))

    for (i, x), (j, y), (k, z) in triples:
        if x != y and y != z and z != x and x + y + z == target:
            yield i, j, k


def three_sum_indices_3(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers. The tuples are yielded in lexicographic order.

    This is the third of four implementations.

    >>> list(three_sum_indices_3([1, 2, 3], [10, 9], [7, 9, 8], 20))
    [(0, 0, 1), (1, 0, 2), (2, 0, 0), (2, 1, 2)]
    >>> next(three_sum_indices_3([0] * 10, [0] * 20, [0] * 30, 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> from itertools import repeat as r
    >>> sum(1 for _ in three_sum_indices_3(r(1, 10), r(2, 20), r(3, 30), 6))
    6000
    """
    xs = list(a)
    ys = list(b)
    zs = list(c)

    return ((i, j, k)
            for i, x in enumerate(xs)
            for j, y in enumerate(ys) if x != y
            for k, z in enumerate(zs)
            if x != z and y != z and x + y + z == target)


def three_sum_indices_4(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers. The tuples are yielded in lexicographic order.

    This is the fourth of four implementations.

    >>> list(three_sum_indices_3([1, 2, 3], [10, 9], [7, 9, 8], 20))
    [(0, 0, 1), (1, 0, 2), (2, 0, 0), (2, 1, 2)]
    >>> next(three_sum_indices_3([0] * 10, [0] * 20, [0] * 30, 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> from itertools import repeat as r
    >>> sum(1 for _ in three_sum_indices_3(r(1, 10), r(2, 20), r(3, 30), 6))
    6000
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


def dot_product(u, v):
    """
    Compute the dot product of real-valued vectors represented as dictionaries.

    The dimension is arbitrarily high (but finite), with keys representing
    components. The dictionaries need not have the same keys. If a key is
    absent, treat it as if the key were present with a value of 0 or 0.0.

    Running time is O(min(len(u), len(v))).

    >>> dot_product({'a': 2, 'b': 3, 'c': 4, 'd': 5}, {'b': 0.5, 'd': 1})
    6.5
    >>> u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
    >>> v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
    >>> w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
    >>> uv = dot_product(u, v)
    >>> round(uv, 2)
    21.56
    >>> uv == dot_product(v, u)
    True
    >>> dot_product(u, w) == dot_product(w, u) == 4.5
    True
    >>> dot_product(v, w) == dot_product(w, v) == 0
    True
    """
    if len(v) < len(u):
        u, v = v, u

    return sum(value * v.get(key, 0) for key, value in u.items())


def flatten2(iterable):
    """
    Flatten an iterable by exactly 2 levels.

    That is, yield sub-sub-elements: elements of elements of elements of the
    argument. If an element of the argument, or an element of an element of the
    argument, isn't iterable, skip it.

    It may be useful to check if an object is iterable by LBYL. You can do this
    by checking if it is considered an instance of collections.abc.Iterable.

    >>> list(flatten2([0, [1, 2], (3, 4, [5, 6, [7]], 8), [9], 10, [{(11,)}]]))
    [5, 6, [7], (11,)]
    >>> next(flatten2([[0, 1, 2], [3, 4, 5], [6, 7, 8]]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> ''.join(flatten2([['foo', 'bar', 'baz'], ['ham', 'spam', 'eggs']]))
    'foobarbazhamspameggs'
    >>> list(flatten2(['hi', [range(5)] * 3, 'bye']))
    ['h', 'i', 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 'b', 'y', 'e']
    >>> list(flatten2(['hi', [iter(range(5))] * 3, 'bye']))
    ['h', 'i', 0, 1, 2, 3, 4, 'b', 'y', 'e']
    >>> list(flatten2('turtles'))  # It's turtles all the way down.
    ['t', 'u', 'r', 't', 'l', 'e', 's']
    """
    return (subsubelement
            for element in iterable if isinstance(element, Iterable)
            for subelement in element if isinstance(subelement, Iterable)
            for subsubelement in subelement)


def ungroup(rows):
    """
    Return a set of all edges in a graph represented by a given adjacency list.

    An adjacency list (sometimes called "adjacency lists") is a jagged table
    that maps vertices to collections of their outward neighbors. That is, when
    a graph has an edge from u to v, its adjacency list's row for u contains v.

    >>> adj1 = {'a': ['b', 'c', 'd'], 'b': ['a', 'd'], 'c': ['a', 'd'], 'd': []}
    >>> ungroup(adj1) == {('a', 'b'), ('a', 'c'), ('a', 'd'),
    ...                   ('b', 'a'), ('b', 'd'), ('c', 'a'), ('c', 'd')}
    True
    >>> adj2 = {1: [2, 3], 2: [4, 5], 3: [6, 7], 4: [8, 9], 5: [], 6: [],
    ...         7: [], 8: [], 9: [2, 5]}
    >>> ungroup(adj2) == {(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7),
    ...                   (4, 8), (4, 9), (9, 2), (9, 5)}
    True
    """
    return {(src, dest) for src, row in rows.items() for dest in row}


def compose_dicts_simple(back, front):
    """
    Given two injective dicts, make one that is their functional composition.

    This is the smallest possible dictionary d with the property that, if front
    associates the key x with the value y, and back associates the key y with
    the value z, then d associates the key x with the value z. Another way to
    say this is that the result dictionary is a pipline through front and back.

    If any value of front is not hashable, raise KeyError. Besides this and
    injectivity, there are no restrictions on either argument's keys or values.

    FIXME: Add doctests.
    """
    return {key: back[value] for key, value in front.items() if value in back}


def compose_dicts(back, front):
    """
    Compose dictionaries, without requiring front to have only hashable values.

    This is like compose_dicts_simple, but arguments' keys and values have no
    restrictions besides injectivity. (Note that, while front may have
    non-hashable values and KeyError must not be raised, such values are
    certain not to be keys of back, because keys must always be hashable.)

    FIXME: Add doctests.
    """
    def in_back(possible_key):
        try:
            return possible_key in back
        except TypeError:
            return False

    return {key: back[value] for key, value in front.items() if in_back(value)}


if __name__ == '__main__':
    import doctest
    doctest.testmod()
