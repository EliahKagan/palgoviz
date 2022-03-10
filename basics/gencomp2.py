#!/usr/bin/env python

"""
More generators and comprehensions.

See also gencomp1.py and fibonacci.py.

Some, but not all, of the exercises in this file benefit from writing
comprehensions with multiple "for" (and sometimes multiple "if") clauses.
"""

from collections.abc import Iterable
import itertools
import operator


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
    my_a = tuple(a)
    my_b = tuple(b)
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
    my_a = tuple(a)
    my_b = tuple(b)
    for x in my_a:
        for y in my_b:
            yield (x, y)


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
    return (y for x in itertools.count() for y in range(x, -1, -1))


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
    my_a = tuple(a)
    my_b = tuple(b)
    my_c = tuple(c)
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
    return set(map(sum, itertools.product(a, b, c)))


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
    labeled_triples = itertools.product(enumerate(a), enumerate(b), enumerate(c))
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
    if len(u) > len(v):  # u should be smaller
        u, v = v, u

    return sum(u_value * v.get(u_key, 0)
               for u_key, u_value in u.items())


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
    return {(source, destination)
            for source, destinations in rows.items()
            for destination in destinations}


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
    return [[i * j for j in range(width + 1)] for i in range(height + 1)]


def compose_dicts_simple(back, front):
    """
    Given two dicts, make one that is their functional composition.

    This is the smallest possible dictionary d with the property that, if front
    associates the key x with the value y, and back associates the key y with
    the value z, then d associates the key x with the value z. Another way to
    say this is that the result dictionary is a pipline through front and back.

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
    >>> status_colors['danger'] = 'vermillion'
    >>> rgb_from_status('danger')
    Traceback (most recent call last):
      ...
    KeyError: 'vermillion'
    >>> status_colors['danger'] = [227, 66, 52]  # RGB values for vermillion.
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

    Return the tranpose of this matrix, in the same form.

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

    return tuple(tuple(matrix[i][j] for i in range(height)) for j in range(width))


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


def _make_affines(w, b):
    return lambda x: w*x + b


def submap(func, rows):
    """
    Map elements of elements of an iterable through a unary function.

    func is a unary function. rows is an iterable of iterables. Return a new
    iterator of iterators whose elements have been mapped through func.

    Conceptually, submap(func, rows)[i][j] == func(rows[i][j]). But neither
    rows nor any of its elements are required to be indexable, only iterable,
    and neither the returned object nor any of its elements are indexable,
    because they are all iterators.

    >>> next(submap(len, []))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> rows = reversed([iter(range(10)), (x - 1 for x in (1, 4, 7)), [2, 3]])
    >>> for mapped_row in submap(lambda x: x**2, rows):
    ...     print(list(mapped_row))
    [4, 9]
    [0, 9, 36]
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> ibm = ['Ifvsjtujdbmmz', 'Qsphsbnnfe', 'BMhpsjuinjd', 'Dpnqvufs']
    >>> ' '.join(map(''.join, submap(lambda c: chr(ord(c) - 1), ibm)))
    'Heuristically Programmed ALgorithmic Computer'
    >>> next(next(submap(len, (([] for _ in range(1)) for _ in range(1)))))
    0
    >>> [list(a) for a in submap(lambda x: x, [iter(range(1, 4))] * 2)]
    [[1, 2, 3], []]
    """
    return (map(func, row) for row in rows)


def is_hermitian(matrix):
    """
    Tell if a complex-valued square matrix (as a nested tuple) is self-adjoint.

    This implementation consists of a single, easily understood, line of code.

    Hint: Does the logic in one of your transpose implementations work on more
    inputs than the description in its docstring guarantees?

    >>> is_hermitian(())
    True
    >>> is_hermitian(((3.3 + 1.2j,),))
    False
    >>> is_hermitian(((3.3 + 0j,),))
    True
    >>> is_hermitian(((1.4 + 2.1j, 3.7 - 6.0j), (3.7 + 6.0j, 1.4 - 2.1j)))
    False
    >>> is_hermitian(((1.4 + 0j, 3.7 - 6.0j), (3.7 - 6.0j, 1.4 + 0j)))
    False
    >>> is_hermitian(((1.4 + 0j, 3.7 - 6.0j), (3.7 + 6.0j, 1.4 + 0j)))
    True
    >>> is_hermitian(((1.4, 3.7 - 6.0j), (3.7 + 6.0j, 1.4)))
    True
    >>> is_hermitian(((0, 0, 1j), (0, 1, 0), (-1j, 0, 0)))
    True
    >>> is_hermitian(((1.7, 0, 3 - 2.1j, 4.4 + 1j),
    ...               (0, -5.9, -7.6j, 0),
    ...               (3 - 2.1j, 7.6j, 17.4, 0.9 - 0.2j),
    ...               (4.4 - 1j, 0, 0.9 + 0.2j, -2.6)))
    False
    >>> is_hermitian(((1.7, 0, 3 - 2.1j, 4.4 + 1j),
    ...               (0, -5.9, -7.6j, 0),
    ...               (3 + 2.1j, 7.6j, 17.4, 0.9 - 0.2j),
    ...               (4.4 - 1j, 0, 0.9 + 0.2j, -2.6)))
    True
    """
    return matrix == transpose(submap(lambda z: z.conjugate(), matrix))


def is_hermitian_alt(matrix):
    """
    Tell if a complex-valued square matrix (as a nested tuple) is self-adjoint.

    This implementation uses O(1) auxiliary space.

    >>> is_hermitian_alt(())
    True
    >>> is_hermitian_alt(((3.3 + 1.2j,),))
    False
    >>> is_hermitian_alt(((3.3 + 0j,),))
    True
    >>> is_hermitian_alt(((1.4 + 2.1j, 3.7 - 6.0j), (3.7 + 6.0j, 1.4 - 2.1j)))
    False
    >>> is_hermitian_alt(((1.4 + 0j, 3.7 - 6.0j), (3.7 - 6.0j, 1.4 + 0j)))
    False
    >>> is_hermitian_alt(((1.4 + 0j, 3.7 - 6.0j), (3.7 + 6.0j, 1.4 + 0j)))
    True
    >>> is_hermitian_alt(((1.4, 3.7 - 6.0j), (3.7 + 6.0j, 1.4)))
    True
    >>> is_hermitian_alt(((0, 0, 1j), (0, 1, 0), (-1j, 0, 0)))
    True
    >>> is_hermitian_alt(((1.7, 0, 3 - 2.1j, 4.4 + 1j),
    ...                   (0, -5.9, -7.6j, 0),
    ...                   (3 - 2.1j, 7.6j, 17.4, 0.9 - 0.2j),
    ...                   (4.4 - 1j, 0, 0.9 + 0.2j, -2.6)))
    False
    >>> is_hermitian_alt(((1.7, 0, 3 - 2.1j, 4.4 + 1j),
    ...                   (0, -5.9, -7.6j, 0),
    ...                   (3 + 2.1j, 7.6j, 17.4, 0.9 - 0.2j),
    ...                   (4.4 - 1j, 0, 0.9 + 0.2j, -2.6)))
    True
    """
    # NOTE: I can't use itertools.combinations_with_replacement or
    #       itertools.product, as they would use O(len(matrix)) space.

    indices = range(len(matrix))

    return all(matrix[i][j].conjugate() == matrix[j][i]
               for i in indices for j in indices)


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
    unique_weights = set(weights)
    unique_biases = set(biases)
    return {_make_affines(w, b) for w in unique_weights for b in unique_biases}


def mean(iterable):
    """
    Find the arithmetic mean (average) of all values in iterable.

    If iterable is empty, raise ZeroDivisionError.

    >>> mean(range(1, 101))
    50.5
    >>> mean(iter([1 - 1j, -1 + 1j]))
    0j
    >>> mean([])
    Traceback (most recent call last):
      ...
    ZeroDivisionError: division by zero
    """
    count = total = 0
    for element in iterable:
        count += 1
        total += element
    return total / count


def floats_in_range(start, stop, step):
    """
    Return an iterator to a range of floating point values.

    The returned object behaves like iter(range(start, stop, step)), except
    that floating point values are accepted. To decrease rounding error,
    previously yielded values are not used to compute subsequent values. New
    values are yielded as long as they are on the same side of the stop value
    as the start value, even if the difference is a small fraction.

    >>> floats_in_range(78.52, 90.85, 0.0)
    Traceback (most recent call last):
      ...
    ValueError: step must not be zero
    >>> [round(x, 3) for x in floats_in_range(78.52, 90.85, 1.27)]
    [78.52, 79.79, 81.06, 82.33, 83.6, 84.87, 86.14, 87.41, 88.68, 89.95]
    >>> next(floats_in_range(78.52, 90.85, -1.27))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> [round(x, 3) for x in floats_in_range(90.85, 78.52, -1.27)]
    [90.85, 89.58, 88.31, 87.04, 85.77, 84.5, 83.23, 81.96, 80.69, 79.42]
    >>> list(floats_in_range(90.85, 78.52, 1.27))
    []
    >>> list(floats_in_range(10.6, 10.6, 0.0000001))
    []
    >>> list(floats_in_range(10.6, 10.6, -0.0000001))
    []
    >>> list(floats_in_range(0, 100_000, 1)) == list(range(100_000))
    True
    >>> list(floats_in_range(1e16, 1e16 + 3, 1))
    [1e+16, 1e+16, 1.0000000000000002e+16]
    """
    if step == 0:
        raise ValueError('step must not be zero')

    comparer = operator.gt if step < 0 else operator.lt

    def generate():
        multiplier = 0

        while comparer((value := start + step * multiplier), stop):
            yield value
            multiplier += 1

    return generate()


def integrate(f, a, b, n):
    """
    Numerically integrate f from a to b, evaluating f at n equidistant points.

    Whether a < b or a > b, evaluate f at a but not b. If a == b, return 0.0.
    Otherwise, if n < 1, raise ValueError.

    Floating point limitations may result in imperfect spacing, and even
    occasionally in evaluating f fewer, or more, than n times. This is okay.

    >>> import math
    >>> round(integrate(math.sin, 0, math.pi, 100), 5)
    1.99984
    >>> round(integrate(math.sin, math.pi, 0, 100), 5)
    -1.99984
    >>> integrate(math.sin, 0, math.pi, 0)
    Traceback (most recent call last):
      ...
    ValueError: can't integrate nonempty domain with no samples
    >>> integrate(math.sin, math.pi, 0, 0)
    Traceback (most recent call last):
      ...
    ValueError: can't integrate nonempty domain with no samples
    >>> integrate(math.sin, math.pi, math.pi, 0)
    0.0
    >>> round(integrate(lambda t: 5 + 2.2 * t, 10, 20, 300), 3)
    379.633
    >>> round(integrate(lambda t: 5 + 2.2 * t, 20, 10, 300), 3)
    -380.367
    """
    if a == b:
        return 0.0
    if n < 1:
        raise ValueError("can't integrate nonempty domain with no samples")

    return mean(f(x) for x in floats_in_range(a, b, (b - a) / n)) * (b - a)


def my_dropwhile(predicate, iterable):
    """
    Yield elements of iterable starting at the first not to satisfy predicate.

    This behaves the same as itertools.dropwhile.

    The is the first of two implementations. It does not use comprehensions.

    >>> next(my_dropwhile(lambda x: x % 17 != 0, iter(range(40, 100))))
    51
    >>> list(my_dropwhile(str.islower, ['foo', 'bar', 'baZ', 'quux']))
    ['baZ', 'quux']
    >>> list(my_dropwhile(str.islower, ['ham', 'spam', 'eggs']))
    []
    >>> list(my_dropwhile(lambda _: False, ()))
    []
    """
    iterator = iter(iterable)

    for value in iterator:
        if not predicate(value):
            break
    else:
        return

    yield value
    yield from iterator


def my_dropwhile_alt(predicate, iterable):
    """
    Yield elements of iterable starting at the first not to satisfy predicate.

    This behaves the same as itertools.dropwhile.

    This is the second of two implementations. It does not use loops.

    >>> next(my_dropwhile_alt(lambda x: x % 17 != 0, iter(range(40, 100))))
    51
    >>> list(my_dropwhile_alt(str.islower, ['foo', 'bar', 'baZ', 'quux']))
    ['baZ', 'quux']
    >>> list(my_dropwhile_alt(str.islower, ['ham', 'spam', 'eggs']))
    []
    >>> list(my_dropwhile_alt(lambda _: False, ()))
    []
    """
    yielding = False
    return (x for x in iterable if yielding or (yielding := not predicate(x)))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
