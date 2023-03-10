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

"""
More generators and comprehensions.

See also gencomp1.py and fibonacci.py.

Some, but not all, of the exercises in this file benefit from writing
comprehensions with multiple "for" (and sometimes multiple "if") clauses.
"""

__all__ = [
    'empty',
    'product_two',
    'product_two_alt',
    'product_two_flexible',
    'pairs',
    'ascending_countdowns',
    'ascending_countdowns_alt',
    'three_sums',
    'three_sums_alt',
    'three_sum_indices_1',
    'three_sum_indices_2',
    'three_sum_indices_3',
    'three_sum_indices_4',
    'dot_product_slow',
    'dot_product',
    'flatten2',
    'ungroup',
    'make_mul_table',
    'compose_dicts_simple',
    'compose_dicts',
    'compose_dicts_view',
    'matrix_square_flat',
    'matrix_square_nested',
    'transpose',
    'transpose_alt',
    'affines',
    'Affine',
    'affines_alt',
    'my_cycle',
    'my_chain',
]

from collections import deque
from collections.abc import Iterable
import itertools


def empty():
    """
    Empty generator.

    >>> it = empty()
    >>> iter(it) is it
    True
    >>> list(it)
    []
    """
    yield from ()


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
    my_a = list(a)
    my_b = list(b)
    return ((x, y) for x in my_a for y in my_b)


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
    my_a = list(a)
    my_b = list(b)
    for x in my_a:
        for y in my_b:
            yield (x, y)


def product_two_flexible(a, b):
    """
    Like product_two above, but a is permitted to be an infinite iterable.

    >>> list(product_two_flexible('hi', 'bye'))
    [('h', 'b'), ('h', 'y'), ('h', 'e'), ('i', 'b'), ('i', 'y'), ('i', 'e')]
    >>> list(product_two_flexible(range(0), range(2)))
    []
    >>> list(product_two_flexible(range(2), range(0)))
    []
    >>> it = product_two_flexible((x - 1 for x in (1, 2)),
    ...                           (x + 5 for x in (3, 4)))
    >>> next(it)
    (0, 8)
    >>> list(it)
    [(0, 9), (1, 8), (1, 9)]
    >>> from itertools import count, islice
    >>> list(islice(product_two_flexible(count(), 'abc'), 7))
    [(0, 'a'), (0, 'b'), (0, 'c'), (1, 'a'), (1, 'b'), (1, 'c'), (2, 'a')]
    >>> list(islice(product_two_flexible(count(), (ch for ch in 'abc')), 7))
    [(0, 'a'), (0, 'b'), (0, 'c'), (1, 'a'), (1, 'b'), (1, 'c'), (2, 'a')]
    """
    my_b = list(b)
    return ((x, y) for x in a for y in my_b)


def pairs(iterable):
    """
    Yield pairs (x, y) where x and y appear in iterable, with x preceding y.

    Pairs are yielded primarily in the order in which x appears, secondarily in
    the order in which y appears. If the input has duplicates, they appear in
    the output. Space usage should decline as the algorithm proceeds. Where r
    is how many pairs remain to yield, the space complexity must be O(sqrt(r)).

    This is like itertools.combinations(iterable, 2), except for the restricted
    space. (Make sure you understand why.) Don't use anything from itertools.

    >>> list(pairs(iter('')))
    []
    >>> next(pairs('A'))  # Likewise empty, fewer than 2 elements.
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(pairs(iter('AB')))
    [('A', 'B')]
    >>> list(pairs('ABC'))
    [('A', 'B'), ('A', 'C'), ('B', 'C')]
    >>> list(pairs(iter('ABCD')))
    [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('C', 'D')]
    >>> list(pairs('AAA'))
    [('A', 'A'), ('A', 'A'), ('A', 'A')]
    """
    queue = deque(iterable)
    while len(queue) > 1:
        x = queue.popleft()
        for y in queue:
            yield x, y


def ascending_countdowns():
    """
    Yield integers counting down to 0 from 0, then from 1, them from 2, etc.

    This implementation returns a generator expression.

    >>> list(itertools.islice(ascending_countdowns(), 25))
    [0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 6, 5, 4, 3]
    >>> sum(itertools.islice(ascending_countdowns(), 1_000_000))
    471108945
    """
    return (y for x in itertools.count() for y in range(x, -1, -1))


def ascending_countdowns_alt():
    """
    Yield integers counting down to 0 from 0, then from 1, them from 2, etc.

    This is like ascending_countdowns above, but implemented as a generator
    function.

    >>> list(itertools.islice(ascending_countdowns_alt(), 25))
    [0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 6, 5, 4, 3]
    >>> sum(itertools.islice(ascending_countdowns_alt(), 1_000_000))
    471108945
    """
    for x in itertools.count():
        yield from range(x, -1, -1)


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
    my_a = list(a)
    my_b = list(b)
    my_c = list(c)
    return {x + y + z for x in my_a for y in my_b for z in my_c}


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
    return {x + y + z for x, y, z in itertools.product(a, b, c)}


def three_sum_indices_1(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers. The tuples are yielded in lexicographic order.

    This is the first of four implementations, which cover all four
    combinations of two independent choices:

    (A) Two implementations return generator expressions and do not contain
        loops. The other two are written as generator functions and do not use
        comprehensions.

    (B) Two implementations use something from itertools to simplify and
        shorten their code, but are slower in some situations (though the worst
        case efficiency is the same). The other two don't do that, instead
        avoiding doing extra work.

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
    my_a = tuple(a)
    my_b = tuple(b)
    my_c = tuple(c)
    for i, x in enumerate(my_a):
        for j, y in enumerate(my_b):
            if x == y:
                continue
            for k, z in enumerate(my_c):
                if y == z or x == z:
                    continue
                if x + y + z == target:
                    yield (i, j, k)


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
    my_a = tuple(a)
    my_b = tuple(b)
    my_c = tuple(c)
    return ((i, j, k)
            for i, x in enumerate(my_a)
            for j, y in enumerate(my_b) if x != y
            for k, z in enumerate(my_c) if y != z and x != z
            if x + y + z == target)


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
    labeled_triples = itertools.product(enumerate(a),
                                        enumerate(b),
                                        enumerate(c))

    for (i, x), (j, y), (k, z) in labeled_triples:
        if x + y + z == target and x != y and x != z and y != z:
            yield (i, j, k)


def three_sum_indices_4(a, b, c, target):
    """
    Make an iterator of tuples (i, j, k) where a[i], b[j], c[k] all differ from
    each other and sum to target.

    This notation is merely illustrative. a, b, and c can be any iterables
    whose elements are numbers. The tuples are yielded in lexicographic order.

    This is the fourth of four implementations.

    >>> list(three_sum_indices_4([1, 2, 3], [10, 9], [7, 9, 8], 20))
    [(0, 0, 1), (1, 0, 2), (2, 0, 0), (2, 1, 2)]
    >>> next(three_sum_indices_4([0] * 10, [0] * 20, [0] * 30, 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> from itertools import repeat as r
    >>> sum(1 for _ in three_sum_indices_4(r(1, 10), r(2, 20), r(3, 30), 6))
    6000
    """
    return ((i, j, k) for (i, x), (j, y), (k, z)
            in itertools.product(enumerate(a), enumerate(b), enumerate(c))
            if x + y + z == target and x != y and x != z and y != z)


def dot_product_slow(u, v):
    """
    Compute the dot product of real-valued vectors represented as dictionaries.

    The dimension is arbitrarily high (but finite), with keys representing
    components. The dictionaries need not have the same keys. If a key is
    absent, treat it as if the key were present with a value of 0 or 0.0.

    Running time is O(len(u) * len(v)).

    >>> dot_product_slow({'a': 2, 'b': 3, 'c': 4, 'd': 5}, {'b': 0.5, 'd': 1})
    6.5
    >>> u = {'s': 1.1, 't': 7.6, 'x': 2.7, 'y': 1.4, 'z': 3.36, 'foo': 9}
    >>> v = {'a': -1, 'y': 3.1, 'x': -4.2, 'bar': 1.9, 'z': 8.5, 'b': 1423.907}
    >>> w = {'p': 8.3, 'q': -0.8, 'r': -2.9, 'foo': 0.5}
    >>> uv = dot_product_slow(u, v)
    >>> round(uv, 2)
    21.56
    >>> uv == dot_product_slow(v, u)
    True
    >>> dot_product_slow(u, w) == dot_product_slow(w, u) == 4.5
    True
    >>> dot_product_slow(v, w) == dot_product_slow(w, v) == 0
    True
    """
    return sum(u_value * v_value
               for (u_key, u_value), (v_key, v_value)
               in itertools.product(u.items(), v.items())
               if v_key == u_key)


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
    small, big = (u, v) if len(u) <= len(v) else (v, u)

    return sum(small_value * big.get(key, 0)
               for key, small_value in small.items())


def flatten2(iterable):
    """
    Flatten an iterable by exactly 2 levels.

    That is, yield sub-sub-elements: elements of elements of elements of the
    argument. If an element of the argument, or an element of an element of the
    argument, isn't iterable, skip it.

    It may be useful to check if an object is iterable by LBYL. You can do this
    by checking if it is considered an instance of collections.abc.Iterable.

    (Such an LBYL check can, technically, give a false negative. A class is a
    subclass of Iterable when it defines __iter__, inherits from Iterable, or
    is registered as a virtual subclass of Iterable. But defining __getitem__
    without __iter__ will also support iteration! This is mostly for backward
    compatibility. Such classes are rare in modern code. When they occur, they
    may not have been intended to support iteration, which may or may not work
    properly. In this function, as in many but not all other cases, it is okay
    to assume objects that aren't instances of Iterable are non-iterable.)

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
    return (sub_sub_element
            for element in iterable if isinstance(element, Iterable)
            for sub_element in element if isinstance(sub_element, Iterable)
            for sub_sub_element in sub_element)


def ungroup(rows):
    """
    Return a set of all edges in a graph represented by a given adjacency list.

    An adjacency list (sometimes called "adjacency lists") is a jagged table
    that maps vertices (sources) to collections of their outward neighbors
    (destinations). That is, when a graph has an edge from u to v, its
    adjacency list's row for u contains v.

    >>> adj1 = {'a': ['b', 'c', 'd'], 'b': ['a', 'd'],
    ...         'c': ['a', 'd'], 'd': []}
    >>> ungroup(adj1) == {('a', 'b'), ('a', 'c'), ('a', 'd'),
    ...                   ('b', 'a'), ('b', 'd'), ('c', 'a'), ('c', 'd')}
    True
    >>> adj2 = {1: [2, 3], 2: [4, 5], 3: [6, 7], 4: [8, 9], 5: [], 6: [],
    ...         7: [], 8: [], 9: [2, 5]}
    >>> ungroup(adj2) == {(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7),
    ...                   (4, 8), (4, 9), (9, 2), (9, 5)}
    True
    """
    return {(key, value) for key, values in rows.items() for value in values}


def make_mul_table(height, width):
    """
    Make a multiplication table from 0 * 0 to height * width, as a nested list.

    make_mul_table(m, n)[i][j] holds i * j; the max i is m, and the max j is n.

    >>> make_mul_table(0, 0)
    [[0]]
    >>> make_mul_table(3, 4)
    [[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8], [0, 3, 6, 9, 12]]
    >>> make_mul_table(4, 3)
    [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 4, 6], [0, 3, 6, 9], [0, 4, 8, 12]]
    >>> make_mul_table(10, 10) == [
    ...     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,   0],
    ...     [0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  10],
    ...     [0,  2,  4,  6,  8, 10, 12, 14, 16, 18,  20],
    ...     [0,  3,  6,  9, 12, 15, 18, 21, 24, 27,  30],
    ...     [0,  4,  8, 12, 16, 20, 24, 28, 32, 36,  40],
    ...     [0,  5, 10, 15, 20, 25, 30, 35, 40, 45,  50],
    ...     [0,  6, 12, 18, 24, 30, 36, 42, 48, 54,  60],
    ...     [0,  7, 14, 21, 28, 35, 42, 49, 56, 63,  70],
    ...     [0,  8, 16, 24, 32, 40, 48, 56, 64, 72,  80],
    ...     [0,  9, 18, 27, 36, 45, 54, 63, 72, 81,  90],
    ...     [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    ... ]
    True
    """
    return [[x * y for y in range(width + 1)] for x in range(height + 1)]


def compose_dicts_simple(back, front):
    """
    Given two dicts, make one that is their functional composition.

    This is the smallest possible dictionary d with the property that, if front
    associates the key x with the value y, and back associates the key y with
    the value z, then d associates the key x with the value z. Another way to
    say this is that the result dictionary is a pipeline through front and
    back.

    Keys in both front and the result should appear in the same order in each.

    If any value of front is not hashable, raise TypeError. There are no other
    restrictions on either argument's keys or values.

    >>> status_colors = dict(unspecified='gray', OK='green', meh='blue',
    ...                      concern='yellow', alarm='orange', danger='red')
    >>> color_rgbs = dict(violet=0xEE82EE, red=0xFF0000, gray=0x808080,
    ...                   black=0x000000, green=0x008000, orange=0xFFA500,
    ...                   azure=0xF0FFFF, yellow=0xFFFF00, blue=0x0000FF)
    >>> status_rgbs = compose_dicts_simple(color_rgbs, status_colors)
    >>> from pprint import pprint
    >>> pprint([f'{c} #{r:06x}' for c, r in status_rgbs.items()], compact=True)
    ['unspecified #808080', 'OK #008000', 'meh #0000ff', 'concern #ffff00',
     'alarm #ffa500', 'danger #ff0000']
    >>> compose_dicts_simple(status_colors, color_rgbs)
    {}
    >>> squares = {x: x**2 for x in range(1, 100)}
    >>> compose_dicts_simple(squares, squares)
    {1: 1, 2: 16, 3: 81, 4: 256, 5: 625, 6: 1296, 7: 2401, 8: 4096, 9: 6561}
    >>> d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
    >>> d2 = {('b', 'c'): 30, None: 20, 'a': 40}
    >>> compose_dicts_simple(d2, d1)
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'list'
    >>> compose_dicts_simple(d1, d2)
    {('b', 'c'): ['d', 'e'], None: ('b', 'c'), 'a': None}
    >>> compose_dicts_simple({}, {42: (set(),)})
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'set'
    """
    return {key: back[value]
            for key, value in front.items() if value in back}


def compose_dicts(back, front):
    """
    Compose dictionaries, without requiring front to have only hashable values.

    This is like compose_dicts_simple, but arguments' keys and values have no
    restrictions. (Note that, while front may have non-hashable values and
    TypeError must not be raised, such values are certain not to be keys of
    back, because keys must always be hashable.)

    >>> status_colors = dict(unspecified='gray', OK='green', meh='blue',
    ...                      concern='yellow', alarm='orange', danger='red')
    >>> color_rgbs = dict(violet=0xEE82EE, red=0xFF0000, gray=0x808080,
    ...                   black=0x000000, green=0x008000, orange=0xFFA500,
    ...                   azure=0xF0FFFF, yellow=0xFFFF00, blue=0x0000FF)
    >>> status_rgbs = compose_dicts(color_rgbs, status_colors)
    >>> from pprint import pprint
    >>> pprint([f'{c} #{r:06x}' for c, r in status_rgbs.items()], compact=True)
    ['unspecified #808080', 'OK #008000', 'meh #0000ff', 'concern #ffff00',
     'alarm #ffa500', 'danger #ff0000']
    >>> compose_dicts(status_colors, color_rgbs)
    {}
    >>> squares = {x: x**2 for x in range(1, 100)}
    >>> compose_dicts(squares, squares)
    {1: 1, 2: 16, 3: 81, 4: 256, 5: 625, 6: 1296, 7: 2401, 8: 4096, 9: 6561}
    >>> d1 = {10: 'a', 20: ('b', 'c'), 30: ['d', 'e'], 40: None}
    >>> d2 = {('b', 'c'): 30, None: 20, 'a': 40}
    >>> compose_dicts(d2, d1)
    {10: 40, 20: 30, 40: 20}
    >>> compose_dicts(d1, d2)
    {('b', 'c'): ['d', 'e'], None: ('b', 'c'), 'a': None}
    >>> compose_dicts({}, {42: (set(),)})
    {}
    """
    d = {}
    for key, value in front.items():
        try:
            d[key] = back[value]
        except (TypeError, KeyError):
            pass

    return d


def compose_dicts_view(back, front):
    """
    Make a function that acts as a view into the composition of back and front.

    Calls to the returned function take O(1) time and behave like subscripting
    the dict returned by a previous call to compose_dicts_simple(back, front),
    except that:

    i.  Changes to back and front are accounted for, even when they occur
        between calls to compose_dicts_view and to the function it returned.

    ii. Errors are raised only when necessary, are deferred as long as
        possible, and reflect what really prevented the operation from
        succeeding.

        That is, if front maps x to y, and y is not a key of back, passing x to
        the returned function raises a KeyError reporting that y (not x) is
        absent. Or, if y is not even hashable, then passing x raises a
        TypeError about y. Other lookups than x, assuming they don't also go
        through y, remain unaffected.

    >>> status_colors = dict(unspecified='gray', OK='green', meh='blue',
    ...                      concern='yellow', alarm='orange', danger='red')
    >>> color_rgbs = dict(violet=0xEE82EE, red=0xFF0000, gray=0x808080,
    ...                   black=0x000000, green=0x008000, orange=0xFFA500,
    ...                   azure=0xF0FFFF, yellow=0xFFFF00, blue=0x0000FF)
    >>> rgb_from_status = compose_dicts_view(color_rgbs, status_colors)
    >>> format(rgb_from_status('OK'), '06X')
    '008000'
    >>> status_colors['OK'] = 'azure'
    >>> format(rgb_from_status('OK'), '06X')
    'F0FFFF'
    >>> status_colors['danger'] = 'vermilion'
    >>> rgb_from_status('danger')
    Traceback (most recent call last):
      ...
    KeyError: 'vermilion'
    >>> status_colors['danger'] = [227, 66, 52]  # RGB values for vermilion.
    >>> rgb_from_status('danger')
    Traceback (most recent call last):
      ...
    TypeError: unhashable type: 'list'
    >>> status_colors['danger'] = 'black'
    >>> format(rgb_from_status('danger'), '06X')
    '000000'
    """
    return lambda key: back[front[key]]


def matrix_square_flat(f, n):
    """
    Square an n-by-n matrix. The result is a dict with index pairs as keys.

    The binary function f, which can be assumed to be fast, represents an
    n-by-n matrix with 1-based indexing, where f(i, j) gives the (i, j) entry.

    Return the matrix product of this n-by-n matrix with itself, as a dict
    whose keys are tuples of the form (i, j), representing the ij entry of the
    product (still using 1-based indexing).

    >>> a = ((0, -1), (-1, 0))
    >>> matrix_square_flat(lambda i, j: a[i - 1][j - 1], 2) == {
    ...     (1, 1): 1, (1, 2): 0,
    ...     (2, 1): 0, (2, 2): 1,
    ... }
    True
    >>> b = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
    >>> matrix_square_flat(lambda i, j: b[i - 1][j - 1], 3) == {
    ...     (1, 1):  30, (1, 2):  36, (1, 3):  42,
    ...     (2, 1):  66, (2, 2):  81, (2, 3):  96,
    ...     (3, 1): 102, (3, 2): 126, (3, 3): 150,
    ... }
    True
    """
    r = range(1, n + 1)
    return {(i, j): sum(f(i, k) * f(k, j) for k in r)
            for i in r for j in r}


def matrix_square_nested(f, n):
    """
    Square an n-by-n matrix. The result is a nested list with 0-based indexing.

    This works like matrix_square_flat above and f still takes 1-based indices,
    but the result is a nested list that, when indexed with i and then with j,
    gives the ij entry of the product, where i and j are 0-based indices.

    >>> a = ((0, -1), (-1, 0))
    >>> matrix_square_nested(lambda i, j: a[i - 1][j - 1], 2)
    [[1, 0], [0, 1]]
    >>> b = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
    >>> matrix_square_nested(lambda i, j: b[i - 1][j - 1], 3)
    [[30, 36, 42], [66, 81, 96], [102, 126, 150]]
    """
    r = range(1, n + 1)
    return [[sum(f(i, k) * f(k, j) for k in r) for j in r] for i in r]


def transpose(matrix):
    """
    Transpose a matrix represented as a tuple of tuples.

    Assume matrix is a tuple of rows, which are themselves tuples, and that
    each row has the same width. Do not assume that width is equal to the
    the height (i.e., the number of rows need not be the number of columns).

    Return the transpose of this matrix, in the same form.

    >>> transpose(((1, 2, 3), (4, 5, 6), (7, 8, 9)))
    ((1, 4, 7), (2, 5, 8), (3, 6, 9))
    >>> transpose(((1, 2), (3, 4), (5, 6)))
    ((1, 3, 5), (2, 4, 6))
    >>> transpose(((1, 2, 3), (4, 5, 6)))
    ((1, 4), (2, 5), (3, 6))
    >>> transpose(())
    ()
    """
    if not matrix:
        return ()

    height = len(matrix)
    width = len(matrix[0])

    return tuple(tuple(matrix[i][j] for i in range(height))
                 for j in range(width))


def transpose_alt(matrix):
    """
    Transpose a matrix represented as a tuple of tuples.

    This is a second independent implementation of transpose. Both behave the
    same on valid input. One uses comprehensions or loops (maybe both). The
    other uses neither comprehensions nor loops and is a single short line.

    >>> transpose_alt(((1, 2, 3), (4, 5, 6), (7, 8, 9)))
    ((1, 4, 7), (2, 5, 8), (3, 6, 9))
    >>> transpose_alt(((1, 2), (3, 4), (5, 6)))
    ((1, 3, 5), (2, 4, 6))
    >>> transpose_alt(((1, 2, 3), (4, 5, 6)))
    ((1, 4), (2, 5), (3, 6))
    >>> transpose_alt(())
    ()
    """
    return tuple(zip(*matrix))


def affines(weights, biases):
    """
    Make a set of all 1-dimensional real-valued affine functions that use a
    weight from weights and a bias from biases.

    A 1-dimensional affine function is a line in the coordinate plane: it takes
    x to wx+b. w is called the coefficient or weight, and b is called the bias.

    Note: All behaviors with combinations of these weights and biases will be
    represented, but no two emitted functions should always behave the same.

    >>> u = [2.3, 1.0, 2.3, -6.5, 5.4]
    >>> v = [1.9, 3.6, -5.1, 1.9]
    >>> s = affines(u, v)
    >>> isinstance(s, set)
    True
    >>> sorted(f(10) for f in s)
    [-70.1, -63.1, -61.4, 4.9, 11.9, 13.6, 17.9, 24.9, 26.6, 48.9, 55.9, 57.6]
    >>> sorted(round(f(5), 1) for f in s)
    [-37.6, -30.6, -28.9, -0.1, 6.4, 6.9, 8.6, 13.4, 15.1, 21.9, 28.9, 30.6]
    >>> t = affines(iter(v), (b for b in u))
    >>> isinstance(t, set)
    True
    >>> sorted(f(5) for f in t)
    [-32.0, -24.5, -23.2, -20.1, 3.0, 10.5, 11.5, 11.8, 14.9, 19.0, 20.3, 23.4]
    >>> sorted(round(f(2), 1) for f in t)
    [-16.7, -9.2, -7.9, -4.8, -2.7, 0.7, 4.8, 6.1, 8.2, 9.2, 9.5, 12.6]
    >>> affines(u, range(0)) == affines((m for m in ()), v) == set()
    True
    """
    def make_affine(w, b):
        return lambda x: w*x + b

    my_biases = set(biases)
    my_weights = set(weights)

    return {make_affine(w, b) for b in my_biases for w in my_weights}


class Affine:
    """
    An extensional notion of a 1-dimensional affine function.

    Instances are "extensional" in the sense that they are equal if and only if
    they return the same value for every value of their argument. This happens
    just when their weights and biases are respectively equal. Functions in
    mathematics are nearly always defined to have extensional equality, while
    functions in programming languages, if they can be compared for equality at
    all, are usually defined to be equal only when they have exactly the same
    code and any associated data, all stored in exactly the same places. (In
    Python, this can be stated more simply: functions are equal when they are
    the same object.) Functions in most programming languages are thus
    intensional rather than extensional.

    In contrast to functions in Python, sets are extensional, in math and in
    Python. Sets are equal if and only if they agree on all "in" queries.

    >>> Affine(-1.5, 6.2)
    Affine(weight=-1.5, bias=6.2)
    >>> _.weight, _.bias
    (-1.5, 6.2)
    >>> Affine(3, -8.2) == Affine(weight=3.0, bias=-8.2)
    True
    >>> Affine(1.1, 2.2)(10)
    13.2
    """

    __slots__ = ('_weight', '_bias')

    def __init__(self, weight, bias):
        """Create an affine transformation with a specified weight and bias."""
        self._weight = weight
        self._bias = bias

    def __call__(self, x):
        """Transform x according to weight and bias."""
        return self.weight*x + self.bias

    def __repr__(self):
        """Represent this Affine as Python code."""
        return (type(self).__name__ +
                f'(weight={self.weight!r}, bias={self.bias!r})')

    def __eq__(self, other):
        """Two Affines are equal if their weights and biases are equal."""
        if not isinstance(other, Affine):
            return NotImplemented
        return self.weight == other.weight and self.bias == other.bias

    def __hash__(self):
        return hash((self.weight, self.bias))

    @property
    def weight(self):
        """Weight or slope by which arguments are dilated."""
        return self._weight

    @property
    def bias(self):
        """Bias or y-intercept by which arguments are offset."""
        return self._bias


def affines_alt(weights, biases):
    """
    Make a set of all 1-dimensional real-valued Affine objects that use a
    weight from weights and a bias from biases.

    These objects represent affine functions in mathematics but are class
    instances, not Python functions. This implementation takes advantage of the
    behavior of Affine instances under equality comparison.

    >>> u = [2.3, 1.0, 2.3, -6.5, 5.4]
    >>> v = [1.9, 3.6, -5.1, 1.9]
    >>> s = affines_alt(u, v)
    >>> isinstance(s, set) and all(isinstance(f, Affine) for f in s)
    True
    >>> sorted(f(10) for f in s)
    [-70.1, -63.1, -61.4, 4.9, 11.9, 13.6, 17.9, 24.9, 26.6, 48.9, 55.9, 57.6]
    >>> sorted(round(f(5), 1) for f in s)
    [-37.6, -30.6, -28.9, -0.1, 6.4, 6.9, 8.6, 13.4, 15.1, 21.9, 28.9, 30.6]
    >>> t = affines_alt(iter(v), (b for b in u))
    >>> isinstance(t, set)
    True
    >>> sorted(f(5) for f in t)
    [-32.0, -24.5, -23.2, -20.1, 3.0, 10.5, 11.5, 11.8, 14.9, 19.0, 20.3, 23.4]
    >>> sorted(round(f(2), 1) for f in t)
    [-16.7, -9.2, -7.9, -4.8, -2.7, 0.7, 4.8, 6.1, 8.2, 9.2, 9.5, 12.6]
    >>> affines_alt(u, range(0)) == affines_alt((m for m in ()), v) == set()
    True
    """
    return {Affine(w, b) for w, b in itertools.product(weights, biases)}


def my_cycle(iterable):
    """
    Repeat an iterable indefinitely. Like itertools.cycle.

    Don't use anything from itertools.

    >>> list(itertools.islice(my_cycle([2, 4, 6]), 25))
    [2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2]
    >>> list(itertools.islice(my_cycle(x * 2 for x in [1, 2, 3]), 25))
    [2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2, 4, 6, 2]
    >>> list(my_cycle(()))
    []
    >>> list(my_cycle(x for x in ()))
    []
    >>> list(itertools.islice(my_cycle(itertools.count(1)), 21))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

    >>> in_it = itertools.zip_longest(itertools.count(), 'ABCDEF')
    >>> out_it = my_cycle(x for pair in in_it for x in pair if x is not None)
    >>> list(itertools.islice(out_it, 19))
    [0, 'A', 1, 'B', 2, 'C', 3, 'D', 4, 'E', 5, 'F', 6, 7, 8, 9, 10, 11, 12]

    >>> it = my_cycle(print(i) for i in range(10, 20))
    >>> next(it) is None
    10
    True
    """
    pool = []

    for element in iterable:
        pool.append(element)
        yield element

    while pool:
        yield from pool


def _from_iterable(iterables):
    return (element for iterable in iterables for element in iterable)


def my_chain(*iterables):
    """
    Chain iterables, as itertools.chain does.

    Don't use anything from itertools (and don't write any classes).

    >>> list(my_chain())
    []
    >>> list(my_chain([1, 2, 3], [], [5, 6], [8, 9, 10], [12, 13]))
    [1, 2, 3, 5, 6, 8, 9, 10, 12, 13]
    >>> list(my_chain(iter([1, 2, 3]), [], [5, 6], iter([8, 9, 10]), [12, 13]))
    [1, 2, 3, 5, 6, 8, 9, 10, 12, 13]
    >>> list(itertools.islice(my_chain(iter('ABC'), itertools.count()), 20))
    ['A', 'B', 'C', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> list(my_chain(*(range(i) for i in range(7))))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5]

    >>> rows = [[], [10, 20, 30], [], [], [], [11, 22, 33], [], []]
    >>> list(my_chain.from_iterable(rows))
    [10, 20, 30, 11, 22, 33]
    >>> list(my_chain.from_iterable(iter(row) for row in rows))
    [10, 20, 30, 11, 22, 33]
    >>> from palgoviz.gencomp1 import windowed
    >>> list(my_chain.from_iterable(windowed(range(10), 3)))
    [0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7, 6, 7, 8, 7, 8, 9]

    >>> it2 = my_chain.from_iterable(range(i) for i in itertools.count())
    >>> list(itertools.islice(it2, 25))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 0, 1, 2, 3]
    >>> it3 = my_chain.from_iterable(windowed(range(1_000_000_000_000_000), 3))
    >>> list(itertools.islice(it3, 25))
    [0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7, 6, 7, 8, 7, 8, 9, 8]
    >>> list(my_chain.from_iterable(() for _ in range(1000)))
    []
    """
    return _from_iterable(iterables)


my_chain.from_iterable = _from_iterable


if __name__ == '__main__':
    import doctest
    doctest.testmod()
