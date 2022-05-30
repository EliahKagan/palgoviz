#!/usr/bin/env python

"""
More generators and comprehensions.

See also gencomp1.py and fibonacci.py.

Some, but not all, of the exercises in this file benefit from writing
comprehensions with multiple "for" (and sometimes multiple "if") clauses.
"""

import collections
from collections.abc import Iterable, Sequence
import itertools
import operator


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


class Empty:
    """
    Empty iterator.

    >>> it = Empty()
    >>> iter(it) is it
    True
    >>> list(it)
    []
    """

    __slots__ = ()

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration()


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


class ProductTwo:
    """
    Like itertools.product, but must be called with exactly two iterables.

    This implementation is as a class (as is itertools.product).

    >>> list(ProductTwo('hi', 'bye'))
    [('h', 'b'), ('h', 'y'), ('h', 'e'), ('i', 'b'), ('i', 'y'), ('i', 'e')]
    >>> list(ProductTwo(range(0), range(2)))
    []
    >>> list(ProductTwo(range(2), range(0)))
    []
    >>> it = ProductTwo((x - 1 for x in (1, 2)), (x + 5 for x in (3, 4)))
    >>> iter(it) is it  # Make sure we have the usual __iter__ for iterators.
    True
    >>> next(it)
    (0, 8)
    >>> list(it)
    [(0, 9), (1, 8), (1, 9)]
    """

    __slots__ = ('_a_elem', '_b', '_a_it', '_b_it')

    def __init__(self, a, b):
        self._a_elem = None
        self._a_it = iter(list(a))
        self._b = list(b)
        self._b_it = Empty()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self._advance()
        except StopIteration:
            self._a_elem = next(self._a_it)
            self._b_it = iter(self._b)
            return self._advance()

    def _advance(self):
        return self._a_elem, next(self._b_it)


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


def prefix_product(sequences, stop):
    """
    Cartesian product of sequences[0], sequences[1], ..., sequences[stop - 1].

    This returns an iterator that yields tuples from the Cartesian product of a
    prefix of sequences, behaving like itertools.product(*sequences[:stop]).
    Like itertools.product, this is lazy. Unlike itertools.product, it requires
    the input iterables to be sequences and does not materialize them. For this
    reason, it uses only O(stop) auxiliary space.

    sequences is assumed to be a sequence of sequences. stop is assumed to be
    an integer in range(len(sequences) + 1). This function is recursive and
    does not use a helper function; it only calls itself.

    >>> list(prefix_product([['a', 'b'], ['x', 'y']], 2))
    [('a', 'x'), ('a', 'y'), ('b', 'x'), ('b', 'y')]
    """
    if stop == 0:
        yield ()
        return

    for prefix_items in prefix_product(sequences, stop - 1):
        for last_item in sequences[stop - 1]:
            yield (*prefix_items, last_item)


def suffix_product(sequences, start):
    """
    Cartesian product of sequences[start], sequences[start + 1], ...,
    sequences[-1].

    This behaves like itertools.product(*sequences[start:]). It uses only
    O(len(sequences) - start) auxiliary space. Like prefix_product above, this
    is recursive and does not use a helper function.

    >>> list(suffix_product([['a', 'b'], ['x', 'y']], 0))
    [('a', 'x'), ('a', 'y'), ('b', 'x'), ('b', 'y')]
    """
    if start == len(sequences):
        yield ()
        return

    for first_item in sequences[start]:
        for suffix_items in suffix_product(sequences, start + 1):
            yield (first_item, *suffix_items)


def my_product(*iterables):
    """
    Cartesian product. Like itertools.product, but with no repeat parameter.

    This implementation uses one of prefix_product or suffix_product for most
    of its functionality. It should use whichever one gives best performance.
    Besides that one function, and builtins, it does not call anything else.

    Beyond not supporting repeat=, this differs from itertools.product in that:

    (1) This is recursive, while itertools.product is iterative. So this fails
        with RecursionError on large len(iterables). itertools.product doesn't.

    (2) itertools.product has a speed advantage due to being implemented in C.

    (3) itertools.product has another speed advantage due to using a different
        algorithm that performs less copying to build up the tuples it yields.

    >>> from pprint import pprint
    >>> pprint(list(my_product('ab', 'cde', 'fg', 'hi')),
    ...        compact=True)
    [('a', 'c', 'f', 'h'), ('a', 'c', 'f', 'i'), ('a', 'c', 'g', 'h'),
     ('a', 'c', 'g', 'i'), ('a', 'd', 'f', 'h'), ('a', 'd', 'f', 'i'),
     ('a', 'd', 'g', 'h'), ('a', 'd', 'g', 'i'), ('a', 'e', 'f', 'h'),
     ('a', 'e', 'f', 'i'), ('a', 'e', 'g', 'h'), ('a', 'e', 'g', 'i'),
     ('b', 'c', 'f', 'h'), ('b', 'c', 'f', 'i'), ('b', 'c', 'g', 'h'),
     ('b', 'c', 'g', 'i'), ('b', 'd', 'f', 'h'), ('b', 'd', 'f', 'i'),
     ('b', 'd', 'g', 'h'), ('b', 'd', 'g', 'i'), ('b', 'e', 'f', 'h'),
     ('b', 'e', 'f', 'i'), ('b', 'e', 'g', 'h'), ('b', 'e', 'g', 'i')]
    >>> pprint(list(my_product(iter('ab'), 'cde', iter('fg'), 'hi')),
    ...        compact=True)
    [('a', 'c', 'f', 'h'), ('a', 'c', 'f', 'i'), ('a', 'c', 'g', 'h'),
     ('a', 'c', 'g', 'i'), ('a', 'd', 'f', 'h'), ('a', 'd', 'f', 'i'),
     ('a', 'd', 'g', 'h'), ('a', 'd', 'g', 'i'), ('a', 'e', 'f', 'h'),
     ('a', 'e', 'f', 'i'), ('a', 'e', 'g', 'h'), ('a', 'e', 'g', 'i'),
     ('b', 'c', 'f', 'h'), ('b', 'c', 'f', 'i'), ('b', 'c', 'g', 'h'),
     ('b', 'c', 'g', 'i'), ('b', 'd', 'f', 'h'), ('b', 'd', 'f', 'i'),
     ('b', 'd', 'g', 'h'), ('b', 'd', 'g', 'i'), ('b', 'e', 'f', 'h'),
     ('b', 'e', 'f', 'i'), ('b', 'e', 'g', 'h'), ('b', 'e', 'g', 'i')]
    >>> from itertools import islice
    >>> sum(map(sum, islice(my_product(*([(0, 1)] * 900)), 10_000)))
    64608
    """
    sequences = [list(iterable) for iterable in iterables]
    return prefix_product(sequences, len(sequences))


def my_product_slow(*iterables):
    """
    Cartesian product. Like itertools.product, but with no repeat parameter.

    This implementation uses whichever of prefix_product or suffix_product is
    not used by my_product. So this is (usually) slower. Like my_product, this
    calls only prefix_product or suffix_product (not both), and maybe builtins.

    >>> from pprint import pprint
    >>> pprint(list(my_product_slow('ab', 'cde', 'fg', 'hi')),
    ...        compact=True)
    [('a', 'c', 'f', 'h'), ('a', 'c', 'f', 'i'), ('a', 'c', 'g', 'h'),
     ('a', 'c', 'g', 'i'), ('a', 'd', 'f', 'h'), ('a', 'd', 'f', 'i'),
     ('a', 'd', 'g', 'h'), ('a', 'd', 'g', 'i'), ('a', 'e', 'f', 'h'),
     ('a', 'e', 'f', 'i'), ('a', 'e', 'g', 'h'), ('a', 'e', 'g', 'i'),
     ('b', 'c', 'f', 'h'), ('b', 'c', 'f', 'i'), ('b', 'c', 'g', 'h'),
     ('b', 'c', 'g', 'i'), ('b', 'd', 'f', 'h'), ('b', 'd', 'f', 'i'),
     ('b', 'd', 'g', 'h'), ('b', 'd', 'g', 'i'), ('b', 'e', 'f', 'h'),
     ('b', 'e', 'f', 'i'), ('b', 'e', 'g', 'h'), ('b', 'e', 'g', 'i')]
    >>> pprint(list(my_product_slow(iter('ab'), 'cde', iter('fg'), 'hi')),
    ...        compact=True)
    [('a', 'c', 'f', 'h'), ('a', 'c', 'f', 'i'), ('a', 'c', 'g', 'h'),
     ('a', 'c', 'g', 'i'), ('a', 'd', 'f', 'h'), ('a', 'd', 'f', 'i'),
     ('a', 'd', 'g', 'h'), ('a', 'd', 'g', 'i'), ('a', 'e', 'f', 'h'),
     ('a', 'e', 'f', 'i'), ('a', 'e', 'g', 'h'), ('a', 'e', 'g', 'i'),
     ('b', 'c', 'f', 'h'), ('b', 'c', 'f', 'i'), ('b', 'c', 'g', 'h'),
     ('b', 'c', 'g', 'i'), ('b', 'd', 'f', 'h'), ('b', 'd', 'f', 'i'),
     ('b', 'd', 'g', 'h'), ('b', 'd', 'g', 'i'), ('b', 'e', 'f', 'h'),
     ('b', 'e', 'f', 'i'), ('b', 'e', 'g', 'h'), ('b', 'e', 'g', 'i')]
    >>> from itertools import islice
    >>> sum(map(sum, islice(my_product_slow(*([(0, 1)] * 90)), 10_000)))
    64608
    """
    sequences = [list(iterable) for iterable in iterables]
    return suffix_product(sequences, 0)


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
    elements = collections.deque(iterable)

    while elements:
        x = elements.popleft()
        for y in elements:
            yield x, y


def ascending_countdowns():
    """
    Yield integers counting down to 0 from 0, then from 1, then from 2, etc.

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


class AscendingCountdowns:
    """
    Yield integers counting down to 0 from 0, then from 1, them from 2, etc.

    This is like ascending_countdowns and ascending_countdowns_alt, but
    implemented as a class.

    >>> from itertools import islice
    >>> it = AscendingCountdowns()
    >>> iter(it) is it  # Make sure we have the usual __iter__ for iterators.
    True
    >>> list(islice(it, 25))
    [0, 1, 0, 2, 1, 0, 3, 2, 1, 0, 4, 3, 2, 1, 0, 5, 4, 3, 2, 1, 0, 6, 5, 4, 3]
    >>> sum(islice(AscendingCountdowns(), 1_000_000))
    471108945
    """

    __slots__ = ('_up', '_down')

    def __init__(self):
        self._up = self._down = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._down < 0:
            self._up += 1
            self._down = self._up

        ret = self._down
        self._down -= 1
        return ret


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

    i.  Two implementations return generator expressions and do not contain
        loops. The other two are written as generator functions and do not use
        comprehensions.

    ii. Two implementations use something from itertools to simplify and
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


def matrix_dimensions(matrix):
    """
    Given a matrix as a nested sequence, return its height and width.

    If matrix is not a sequence of sequences, raise TypeError.

    If matrix is empty, or has any empty rows, raise ValueError.

    If matrix is jagged--that is, its rows differ in width--raise ValueError.

    >>> matrix_dimensions(((0, -1), (-1, 0)))
    (2, 2)
    >>> matrix_dimensions([[1, 2], [3, 4], [5, 6]])
    (3, 2)
    >>> matrix_dimensions([(1, 2, 3), 'ABC'])
    (2, 3)
    >>> matrix_dimensions([])
    Traceback (most recent call last):
      ...
    ValueError: empty matrix not supported
    >>> matrix_dimensions([[], []])
    Traceback (most recent call last):
      ...
    ValueError: zero-width nonempty matrix not supported
    >>> matrix_dimensions([[3, 4], [5]])
    Traceback (most recent call last):
      ...
    ValueError: jagged grid not supported (must be rectangular)
    >>> matrix_dimensions([[4], [], [5]])
    Traceback (most recent call last):
      ...
    ValueError: jagged grid not supported (must be rectangular)
    >>> matrix_dimensions(3)
    Traceback (most recent call last):
      ...
    TypeError: matrix is not a sequence
    >>> matrix_dimensions([[4], [], {10, 20}])
    Traceback (most recent call last):
      ...
    TypeError: row is not a sequence
    """
    if not isinstance(matrix, Sequence):
        raise TypeError('matrix is not a sequence')

    if not all(isinstance(row, Sequence) for row in matrix):
        raise TypeError('row is not a sequence')

    height = len(matrix)
    if height == 0:
        raise ValueError('empty matrix not supported')

    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError('jagged grid not supported (must be rectangular)')
    if width == 0:
        raise ValueError('zero-width nonempty matrix not supported')

    return height, width


def matrix_multiply(a, b):
    """
    Given matrices as nested sequences, compute their product as a nested list.

    Use matrix_dimensions to check that they are well-formed and find their
    heights and widths. Retain its prohibition on empty matrices. In addition
    to any exceptions it may raise, raise ValueError if a and b are well-formed
    matrices that cannot be multiplied due to incompatible dimensions.

    # FIXME: Needs tests.
    """
    m, n = matrix_dimensions(a)
    n_, p = matrix_dimensions(b)
    if n != n_:
        raise ValueError(
            f"can't multiply {n}-column matrix by {n_}-row matrix")

    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(p)]
            for i in range(m)]


def identity_matrix(n):
    """
    Make an n-by-n identity matrix, represented as a nested list.

    This implementation is self-contained (except that it may use builtins) and
    consists of a single statement, which fits easily on one line.

    >>> identity_matrix(0)
    []
    >>> identity_matrix(1)
    [[1]]
    >>> identity_matrix(2)
    [[1, 0], [0, 1]]
    >>> identity_matrix(3)
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    >>> identity_matrix(4)
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    >>> from pprint import pprint
    >>> pprint(identity_matrix(15))
    [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]
    """
    return [[int(i == j) for j in range(n)] for i in range(n)]


def _kronecker_delta(i, j):
    """Kronecker delta. Compute the (i, j) entry of an identity matrix."""
    return int(i == j)


def _identity_matrix_row(n, i):
    """Return the ith row of an n-by-n identity matrix (0-based indexing)."""
    return [_kronecker_delta(i, j) for j in range(n)]


def identity_matrix_alt(n):
    """
    Make an n-by-n identity matrix, represented as a nested list.

    This alternative implementation uses a helper function that computes a row,
    which itself uses a helper function that computes an entry. Both helpers
    should be written as top-level functions, with tests in test_gencomp2.py.

    >>> identity_matrix_alt(0)
    []
    >>> identity_matrix_alt(1)
    [[1]]
    >>> identity_matrix_alt(2)
    [[1, 0], [0, 1]]
    >>> identity_matrix_alt(3)
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    >>> identity_matrix_alt(4)
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    >>> from pprint import pprint
    >>> pprint(identity_matrix_alt(15))
    [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]
    """
    return [_identity_matrix_row(n, i) for i in range(n)]


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
    return tuple(zip(*matrix))


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
    if not matrix:
        return ()

    height = len(matrix)
    width = len(matrix[0])

    return tuple(tuple(matrix[i][j] for i in range(height)) for j in range(width))


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
    return all(matrix[i][j] == matrix[j][i].conjugate()
               for i in range(len(matrix))
               for j in range(i + 1))


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

    compare = (operator.gt if step < 0 else operator.lt)
    values = (start + step * i for i in itertools.count())
    return itertools.takewhile(lambda value: compare(value, stop), values)


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


def my_takewhile(predicate, iterable):
    """
    Yield elements of iterable until some element does not satisfy predicate.

    This behaves the same as itertools.takewhile.

    >>> next(my_takewhile(lambda _: True, []))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(my_takewhile(lambda x: x < 10, range(1, 1_000_000_000_000_000)))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(my_takewhile(lambda x: x, iter([3, {12}, [], 4, 'abc'])))
    [3, {12}]
    >>> words = ['foo', 'bar', 'baz', 'quux', 'ham', 'egg', 'spam', 'foobar']
    >>> list(my_takewhile(lambda a: len(a) == 3, map(str.upper, words)))
    ['FOO', 'BAR', 'BAZ']
    """
    for element in iterable:
        if not predicate(element):
            break
        yield element


def my_dropwhile(predicate, iterable):
    """
    Yield elements of iterable starting at the first not to satisfy predicate.

    This behaves the same as itertools.dropwhile.

    Consider: Can takewhile be used to implement dropwhile? Why or why not?

    This is the first of two implementations. It does not use comprehensions.

    >>> next(my_dropwhile(lambda x: x % 17 != 0, iter(range(40, 100))))
    51
    >>> list(my_dropwhile(str.islower, ['foo', 'bar', 'baZ', 'quux']))
    ['baZ', 'quux']
    >>> list(my_dropwhile(str.islower, ['ham', 'spam', 'eggs']))
    []
    >>> list(my_dropwhile(lambda _: False, ()))
    []
    """
    it = iter(iterable)

    for item in it:
        if not predicate(item):
            yield item
            break

    yield from it


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


def outdegrees(rows):
    """
    Given an adjacency list, make a Counter that maps vertices to outdegrees.

    rows is a directed graph's adjacency list, supplied as a dictionary (see
    ungroup, above). The outdegree (or out-degree) of a vertex is how many
    forward neighbors it has, i.e., the number of edges coming out of the
    vertex.

    Your algorithm should have the best possible worst-case asymptotic time
    complexity. [Please write the running time, for n nodes and m edges, here.]

    Note: This can, and probably should, be done with a single line of code.

    FIXME: Needs tests.
    """
    return collections.Counter({src: len(row) for src, row in rows.items()})


def indegrees(rows):
    """
    Given an adjacency list, make a Counter that maps vertices to indegrees.

    rows is a directed graph's adjacency list, supplied as a dictionary (as
    described above). The indegree (or in-degree) of a vertex is how many
    backward (i.e., reverse) neighbors it has; i.e., how many vertices have it
    as a forward neighbor; i.e., the number of edges coming into the vertex.

    Your algorithm should have the best possible worst-case asymptotic time
    complexity. [Please write the running time, for n nodes and m edges, here.]

    Note: This can, and probably should, be done with a single line of code.

    FIXME: Needs tests.
    """
    return collections.Counter(itertools.chain.from_iterable(rows.values()))


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
    history = []

    for item in iterable:
        yield item
        history.append(item)

    if history:
        while True:
            yield from history


def _chain_from_iterable(iterables):
    """Iterate an iterable of iterables and chain those iterables."""
    return (element for iterable in iterables for element in iterable)


def my_chain(*iterables):
    """
    Chain iterables, as itertools.chain does.

    Don't use anything from itertools (and don't write any classes).

    >>> list(my_chain())
    []
    >>> list(my_chain([1, 2, 3], [5, 6], [8, 9, 10], [12, 13]))
    [1, 2, 3, 5, 6, 8, 9, 10, 12, 13]
    >>> list(my_chain(iter([1, 2, 3]), [5, 6], iter([8, 9, 10]), [12, 13]))
    [1, 2, 3, 5, 6, 8, 9, 10, 12, 13]
    >>> list(itertools.islice(my_chain(iter('ABC'), itertools.count()), 20))
    ['A', 'B', 'C', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    >>> list(my_chain(*(range(i) for i in range(7))))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5]

    >>> list(my_chain.from_iterable([[10, 20, 30], [11, 22, 33]]))
    [10, 20, 30, 11, 22, 33]
    >>> it1 = iter([iter([10, 20, 30]), iter([11, 22, 33])])
    >>> list(my_chain.from_iterable(it1))
    [10, 20, 30, 11, 22, 33]
    >>> from gencomp1 import windowed
    >>> list(my_chain.from_iterable(windowed(range(10), 3)))
    [0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7, 6, 7, 8, 7, 8, 9]

    >>> it2 = my_chain.from_iterable(range(i) for i in itertools.count())
    >>> list(itertools.islice(it2, 25))
    [0, 0, 1, 0, 1, 2, 0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 5, 0, 1, 2, 3]
    >>> it3 = my_chain.from_iterable(windowed(range(1_000_000_000_000_000), 3))
    >>> list(itertools.islice(it3, 25))
    [0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7, 6, 7, 8, 7, 8, 9, 8]
    """
    return _chain_from_iterable(iterables)


my_chain.from_iterable = _chain_from_iterable


_ALPHA_LEN = 26
"""Number of distinct letters in the English alphabet."""


def encrypt(key, cleartext):
    """
    Encrypt a message with a polyalphabetic cipher.

    The key is an iterable of one or more integers in range(26). The message,
    cleartext, is a string that may be assumed to consist only of unaccented
    lower-case English letters. The kth letter of the resulting ciphertext is
    obtained by cycling the kth letter of cleartext around the alphabet by the
    number of positions indicated by the kth element of key, except that if you
    run out of elements of key, reuse the key starting from the beginning.

    FIXME: Needs tests.
    """
    return ''.join(chr(ord('a') + (ord(ch) - ord('a') + r) % _ALPHA_LEN)
                   for r, ch in zip(itertools.cycle(key), cleartext))


def decrypt(key, ciphertext):
    """
    Decrypt a message encrypted (as by encrypt) with a polyalphabetic cipher.

    FIXME: Needs tests.
    """
    return encrypt((_ALPHA_LEN - r for r in key), ciphertext)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
