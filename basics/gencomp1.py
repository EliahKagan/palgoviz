#!/usr/bin/env python

"""
Generators and comprehensions.

See also gencomp2.py and fibonacci.py.
"""

import collections
import contextlib
import itertools

import more_itertools

from util import identity_function


def my_enumerate(iterable, start=0):
    """
    Pair up items with indices. Like the built-in enumerate.

    >>> men = my_enumerate(range(3,10000))
    >>> next(men)
    (0, 3)
    >>> next(men)
    (1, 4)
    >>> next(men)
    (2, 5)
    >>> next(men)
    (3, 6)
    >>> list(my_enumerate(['ham', 'spam', 'eggs']))
    [(0, 'ham'), (1, 'spam'), (2, 'eggs')]
    >>> men = my_enumerate(range(3,10000), 3)
    >>> next(men)
    (3, 3)
    >>> next(men)
    (4, 4)
    >>> next(men)
    (5, 5)
    >>> next(men)
    (6, 6)
    >>> list(my_enumerate(['ham', 'spam', 'eggs'], 10))
    [(10, 'ham'), (11, 'spam'), (12, 'eggs')]
    """
    return zip(itertools.count(start), iterable)


def my_enumerate_alt(iterable, start=0):
    """
    Pair up items with indices, without using zip, enumerate, or itertools.

    >>> men = my_enumerate_alt(range(3,10000))
    >>> next(men)
    (0, 3)
    >>> next(men)
    (1, 4)
    >>> next(men)
    (2, 5)
    >>> next(men)
    (3, 6)
    >>> list(my_enumerate_alt(['ham', 'spam', 'eggs']))
    [(0, 'ham'), (1, 'spam'), (2, 'eggs')]
    >>> men = my_enumerate_alt(range(3,10000), 3)
    >>> next(men)
    (3, 3)
    >>> next(men)
    (4, 4)
    >>> next(men)
    (5, 5)
    >>> next(men)
    (6, 6)
    >>> list(my_enumerate_alt(['ham', 'spam', 'eggs'], 10))
    [(10, 'ham'), (11, 'spam'), (12, 'eggs')]
    """
    count = start
    for element in iterable:
        yield count, element
        count += 1


class Enumerate:
    """
    Iterator that pairs items with indices.

    This is like the built-in enumerate, including that it is implemented as a
    class rather than as a function. Do not use zip, enumerate, or itertools.

    >>> men = Enumerate(range(3,10000))
    >>> next(men)
    (0, 3)
    >>> next(men)
    (1, 4)
    >>> next(men)
    (2, 5)
    >>> next(men)
    (3, 6)
    >>> list(Enumerate(['ham', 'spam', 'eggs']))
    [(0, 'ham'), (1, 'spam'), (2, 'eggs')]
    >>> men = Enumerate(range(3,10000), 3)
    >>> next(men)
    (3, 3)
    >>> next(men)
    (4, 4)
    >>> next(men)
    (5, 5)
    >>> next(men)
    (6, 6)
    >>> list(Enumerate(['ham', 'spam', 'eggs'], 10))
    [(10, 'ham'), (11, 'spam'), (12, 'eggs')]
    """

    __slots__ = ('_index', '_iterator')

    def __init__(self, iterable, start=0):
        self._index = start
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self._iterator)
        index = self._index
        self._index += 1
        return index, value


def print_enumerated(*, start=0):
    """
    Show the effect of my_enumerate on a sequence of 5, ..., 9 (inclusive).

    (Due to "*", "start" is now a keyword-only argument, meaning the caller
    MUST use the form print_enumerated(start=n) to pass it.)

    >>> print_enumerated()
    index = 0, value = 5
    index = 1, value = 6
    index = 2, value = 7
    index = 3, value = 8
    index = 4, value = 9
    >>> print_enumerated(start=7)
    index = 7, value = 5
    index = 8, value = 6
    index = 9, value = 7
    index = 10, value = 8
    index = 11, value = 9
    """
    for index, value in my_enumerate(range(5, 10), start):
        print(f'{index = }, {value = }')


def print_enumerated_alt(*, start=0):
    """
    Alternative implementation of print_enumerated.

    This uses a generator expression. It also uses Enumerate, not my_enumerate.

    >>> print_enumerated_alt()
    index = 0, value = 5
    index = 1, value = 6
    index = 2, value = 7
    index = 3, value = 8
    index = 4, value = 9
    >>> print_enumerated_alt(start=7)
    index = 7, value = 5
    index = 8, value = 6
    index = 9, value = 7
    index = 10, value = 8
    index = 11, value = 9
    """
    lines = (f'{index = }, {value = }'
             for index, value
             in Enumerate(range(5, 10), start))

    for line in lines:
        print(line)


def my_any(iterable):
    """
    Test if any element of an iterable is truthy.

    >>> my_any([])
    False
    >>> my_any([17, 4, 9, 0, 3, 5, 0])
    True
    >>> my_any(x % 17 == 0 for x in range(100))
    True
    >>> my_any(x > 100 for x in range(100))
    False
    """
    return next((True for element in iterable if element), False)


def my_any_alt(iterable):
    """
    Test if any element of an iterable is truthy, using no comprehensions.

    >>> my_any_alt([])
    False
    >>> my_any_alt([17, 4, 9, 0, 3, 5, 0])
    True
    >>> my_any_alt(x % 17 == 0 for x in range(100))
    True
    >>> my_any_alt(x > 100 for x in range(100))
    False
    """
    for element in iterable:
        if element:
            return True
    return False


def my_all(iterable):
    """
    Tell if all elements of an iterable are truthy.

    >>> my_all([])
    True
    >>> my_all([17, 4, 9, 0, 3, 5, 0])
    False
    >>> my_all(x % 17 == 0 for x in range(100))
    False
    >>> my_all(x > 100 for x in range(100))
    False
    >>> my_all(x % 17 == 0 for x in range(0, 100, 17))
    True
    >>> my_all([1])
    True
    >>> my_all([1, 1, 1, 6, 7])
    True
    """
    return next((False for element in iterable if not element), True)


def my_all_alt(iterable):
    """
    Test if all elements of an iterable are truthy, using no comprehensions.

    >>> my_all_alt([])
    True
    >>> my_all_alt([17, 4, 9, 0, 3, 5, 0])
    False
    >>> my_all_alt(x % 17 == 0 for x in range(100))
    False
    >>> my_all_alt(x > 100 for x in range(100))
    False
    >>> my_all_alt(x % 17 == 0 for x in range(0, 100, 17))
    True
    >>> my_all_alt([1])
    True
    >>> my_all_alt([1, 1, 1, 6, 7])
    True
    """
    for element in iterable:
        if not element:
            return False
    return True


def zip_two(first, second):
    """
    Zip two iterables.

    Zips shortest like the built-in zip, but must take exactly 2 arguments.

    >>> list(zip_two([], []))
    []
    >>> list(zip_two([10, 20], []))
    []
    >>> list(zip_two([], [30, 40]))
    []

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!
    I ordered a 4k monitor but I got a gigantic bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat']
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> bobcats = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> received = (cat.upper() for cat in bobcats)
    >>> for order, got in zip_two(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a BOBCAT instead!
    I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!
    """
    f = iter(first)
    s = iter(second)
    with contextlib.suppress(StopIteration):
        while True:
            yield (next(f), next(s))


class ZipTwo:
    """
    Zip two iterables. Like zip_two, but implemented as a class.

    Zips shortest like the built-in zip, but must take exactly 2 arguments.

    >>> list(ZipTwo([], []))
    []
    >>> list(ZipTwo([10, 20], []))
    []
    >>> list(ZipTwo([], [30, 40]))
    []

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in ZipTwo(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!
    I ordered a 4k monitor but I got a gigantic bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat']
    >>> for order, got in ZipTwo(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in ZipTwo(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> bobcats = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> received = (cat.upper() for cat in bobcats)
    >>> for order, got in ZipTwo(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a BOBCAT instead!
    I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!
    """

    __slots__ = ('_done', '_iterator1', '_iterator2')

    def __init__(self, iterable1, iterable2):
        self._done = False
        self._iterator1 = iter(iterable1)
        self._iterator2 = iter(iterable2)

    def __iter__(self):
        return self

    def __next__(self):
        if self._done:
            raise StopIteration()

        try:
            return next(self._iterator1), next(self._iterator2)
        except StopIteration:
            self._done = True
            raise


def my_zip(*iterables):
    """
    Zip any number of iterables.

    This is like the built-in zip, but with no "strict" argument.

    >>> list(my_zip([], []))
    []
    >>> list(my_zip([10, 20], []))
    []
    >>> list(my_zip([], [30, 40]))
    []
    >>> list(my_zip([]))
    []
    >>> list(my_zip(()))
    []
    >>> list(my_zip([10]))
    [(10,)]
    >>> list(my_zip())
    []

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!
    I ordered a 4k monitor but I got a gigantic bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat']
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> bobcats = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> received = (cat.upper() for cat in bobcats)
    >>> for order, got in my_zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a BOBCAT instead!
    I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = (cat.upper() for cat in bobcats)
    >>> grunts = ['Doh!', 'Ow!', 'OOF!']
    >>> for grunt, order, got in my_zip(grunts, ordered, received):
    ...     print(f'{grunt} I ordered a {order} but I got a {got} instead!')
    Doh! I ordered a gaming mouse but I got a BOBCAT instead!
    Ow! I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    OOF! I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = (cat.upper() for cat in bobcats)
    >>> grunts = ['Doh!', 'Ow!', 'OOF!']
    >>> for grunt, order, got in my_zip(grunts, ordered, received):
    ...     print(f'{grunt} I ordered a {order} but I got a {got} instead!')
    Doh! I ordered a gaming mouse but I got a BOBCAT instead!
    Ow! I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    """
    if not iterables:  # Check if there are no arguments.
        return

    iterators = [iter(arg) for arg in iterables]

    with contextlib.suppress(StopIteration):
        while True:
            # StopIteration cannot propagate out from a generator object,
            # therefore, we use a list comprehension. If it could, the tuple
            # constructor would incorrectly interpret the StopIteration as
            # indicating we have exhausted the generator object, whereas what
            # it would indicate is that one of the iterators in the generator
            # expression is exhausted.
            yield tuple([next(it) for it in iterators])


class Zip:
    """
    Zip any number of iterables. Like my_zip, but implemented as a class.

    This is like the built-in zip, but with no "strict" argument.

    >>> list(Zip([], []))
    []
    >>> list(Zip([10, 20], []))
    []
    >>> list(Zip([], [30, 40]))
    []
    >>> list(Zip([]))
    []
    >>> list(Zip(()))
    []
    >>> list(Zip([10]))
    [(10,)]
    >>> list(Zip())
    []

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in Zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!
    I ordered a 4k monitor but I got a gigantic bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = ['bobcat', 'larger bobcat']
    >>> for order, got in Zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> for order, got in Zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a bobcat instead!
    I ordered a mechanical keyboard but I got a larger bobcat instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> bobcats = ['bobcat', 'larger bobcat', 'gigantic bobcat']
    >>> received = (cat.upper() for cat in bobcats)
    >>> for order, got in Zip(ordered, received):
    ...     print(f'I ordered a {order} but I got a {got} instead!')
    I ordered a gaming mouse but I got a BOBCAT instead!
    I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard', '4k monitor']
    >>> received = (cat.upper() for cat in bobcats)
    >>> grunts = ['Doh!', 'Ow!', 'OOF!']
    >>> for grunt, order, got in Zip(grunts, ordered, received):
    ...     print(f'{grunt} I ordered a {order} but I got a {got} instead!')
    Doh! I ordered a gaming mouse but I got a BOBCAT instead!
    Ow! I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    OOF! I ordered a 4k monitor but I got a GIGANTIC BOBCAT instead!

    >>> ordered = ['gaming mouse', 'mechanical keyboard']
    >>> received = (cat.upper() for cat in bobcats)
    >>> grunts = ['Doh!', 'Ow!', 'OOF!']
    >>> for grunt, order, got in Zip(grunts, ordered, received):
    ...     print(f'{grunt} I ordered a {order} but I got a {got} instead!')
    Doh! I ordered a gaming mouse but I got a BOBCAT instead!
    Ow! I ordered a mechanical keyboard but I got a LARGER BOBCAT instead!
    """

    __slots__ = ('_done', '_iterators')

    def __init__(self, *iterables):
        self._done = not iterables
        self._iterators = [iter(iterable) for iterable in iterables]

    def __iter__(self):
        return self

    def __next__(self):
        if self._done:
            raise StopIteration()

        try:
            # Use a list comprehension, so that StopIteration can be propagated
            # out of it and be caught in this function. From a generator
            # expression, StopIteration converts to RuntimeError (which should
            # not be caught). In map, StopIteration is confused with the map
            # itself being exhausted. [This is an alternative description of
            # the same situation as in the yield statement in my_zip, above.]
            return tuple([next(iterator) for iterator in self._iterators])
        except StopIteration:
            self._done = True
            raise


def print_zipped():
    """
    Zip two enumerated things with my_enumerate and zip_two and print elements.

    >>> print_zipped()
    word_index=1, word='bat', number_index=100, number=1.5
    word_index=2, word='dog', number_index=101, number=2.5
    word_index=3, word='cat', number_index=102, number=3.5
    word_index=4, word='horse', number_index=103, number=4.5
    """
    words = ['bat', 'dog', 'cat', 'horse']
    numbers = [1.5, 2.5, 3.5, 4.5]
    zipped = zip_two(my_enumerate(words, 1), my_enumerate(numbers, 100))

    for (word_index, word), (number_index, number) in zipped:
        print(f'{word_index=}, {word=}, {number_index=}, {number=}')


def _validate_take(n):
    """Shared validation logic for take and take_good functions."""
    if not isinstance(n, int):
        raise TypeError('n must be an int')
    if n < 0:
        raise ValueError("can't yield negatively many items")


def take_good(iterable, n):
    """
    Yield the first n elements of iterable, or all if there are fewer than n.

    This implementation uses something in itertools to do almost all its work.

    >>> next(take_good(range(3), 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(take_good(range(3), 1))
    [0]
    >>> list(take_good(range(3), 2))
    [0, 1]
    >>> list(take_good(range(3), 3))
    [0, 1, 2]
    >>> list(take_good(range(3), 4))
    [0, 1, 2]
    >>> list(take_good(range(3), 1_000_000))
    [0, 1, 2]
    >>> it = take_good((x**2 for x in itertools.count(2)), 2)
    >>> next(it)
    4
    >>> next(it)
    9
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> take_good(range(5), -1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> take_good(range(5), -1)
    Traceback (most recent call last):
      ...
    ValueError: can't yield negatively many items
    >>> list(take_good('pqr', True))  # OK, since bool is a subclass of int.
    ['p']
    >>> it = (x**2 for x in range(1, 6))
    >>> list(take_good(it, 2))
    [1, 4]
    >>> list(it)  # Make sure we didn't consume too much.
    [9, 16, 25]
    """
    _validate_take(n)
    return itertools.islice(iterable, n)


def take(iterable, n):
    """
    Yield the first n elements of iterable, or all if there are fewer than n.

    Unlike take_good, this implementation does not use anything from itertools.

    >>> next(take(range(3), 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(take(range(3), 1))
    [0]
    >>> list(take(range(3), 2))
    [0, 1]
    >>> list(take(range(3), 3))
    [0, 1, 2]
    >>> list(take(range(3), 4))
    [0, 1, 2]
    >>> list(take(range(3), 1_000_000))
    [0, 1, 2]
    >>> it = take((x**2 for x in itertools.count(2)), 2)
    >>> next(it)
    4
    >>> next(it)
    9
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> take(range(5), -1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> take(range(5), -1)
    Traceback (most recent call last):
      ...
    ValueError: can't yield negatively many items
    >>> list(take('pqr', True))  # OK, since bool is a subclass of int.
    ['p']
    >>> it = (x**2 for x in range(1, 6))
    >>> list(take(it, 2))
    [1, 4]
    >>> list(it)  # Make sure we didn't consume too much.
    [9, 16, 25]
    """
    _validate_take(n)
    return (element for _, element in zip(range(n), iterable))


class Take:
    """
    Iterator to the first n elements of iterable, or all if it doesn't have n.

    This is like take, but implemented as a class. (Please don't call islice.)

    >>> next(Take(range(3), 0))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(Take(range(3), 1))
    [0]
    >>> list(Take(range(3), 2))
    [0, 1]
    >>> list(Take(range(3), 3))
    [0, 1, 2]
    >>> list(Take(range(3), 4))
    [0, 1, 2]
    >>> list(Take(range(3), 1_000_000))
    [0, 1, 2]
    >>> it = Take((x**2 for x in itertools.count(2)), 2)
    >>> next(it)
    4
    >>> next(it)
    9
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> Take(range(5), -1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> Take(range(5), -1)
    Traceback (most recent call last):
      ...
    ValueError: can't yield negatively many items
    >>> list(Take('pqr', True))  # OK, since bool is a subclass of int.
    ['p']
    >>> it = (x**2 for x in range(1, 6))
    >>> list(Take(it, 2))
    [1, 4]
    >>> list(it)  # Make sure we didn't consume too much.
    [9, 16, 25]
    """

    __slots__ = ('_remaining', '_iterator')

    def __init__(self, iterable, n):
        _validate_take(n)
        self._remaining = n
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        assert self._remaining >= 0
        if self._remaining == 0:
            raise StopIteration()
        self._remaining -= 1
        return next(self._iterator)


def _validate_drop(n):
    """Shared validation logic for drop and drop_good functions."""
    if not isinstance(n, int):
        raise TypeError('n must be an int')
    if n < 0:
        raise ValueError("can't skip negatively many items")


def drop_good(iterable, n):
    """
    Skip the first n elements of iterable (or all if fewer). Yield the rest.

    This implementation uses something in itertools to do most of its work, and
    there are no restrictions on what or how it uses things from itertools.

    >>> list(drop_good(range(5), 0))
    [0, 1, 2, 3, 4]
    >>> list(drop_good(range(5), 1))
    [1, 2, 3, 4]
    >>> list(drop_good(range(5), 2))
    [2, 3, 4]
    >>> list(drop_good(range(5), 4))
    [4]
    >>> list(drop_good(range(5), 5))
    []
    >>> list(drop_good(range(5), 6))
    []
    >>> list(drop_good(range(5), 1_000_000))
    []
    >>> it = take(drop_good(itertools.count(1), 1000), 2)
    >>> next(it)
    1001
    >>> next(it)
    1002
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> drop_good(range(5), -1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> drop_good(range(5), -1)
    Traceback (most recent call last):
      ...
    ValueError: can't skip negatively many items
    >>> list(drop_good('pqr', True))  # OK, since bool is a subclass of int.
    ['q', 'r']
    """
    _validate_drop(n)
    return itertools.islice(iterable, n, None)


def drop(iterable, n):
    """
    Skip the first n elements of iterable (or all if fewer). Yield the rest.

    Unlike drop_good, this implementation may only use up to one function/class
    from itertools, and if that class is islice, it may not call it with more
    than two arguments.

    >>> list(drop(range(5), 0))
    [0, 1, 2, 3, 4]
    >>> list(drop(range(5), 1))
    [1, 2, 3, 4]
    >>> list(drop(range(5), 2))
    [2, 3, 4]
    >>> list(drop(range(5), 4))
    [4]
    >>> list(drop(range(5), 5))
    []
    >>> list(drop(range(5), 6))
    []
    >>> list(drop(range(5), 1_000_000))
    []
    >>> it = take(drop(itertools.count(1), 1000), 2)
    >>> next(it)
    1001
    >>> next(it)
    1002
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> drop(range(5), -1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> drop(range(5), -1)
    Traceback (most recent call last):
      ...
    ValueError: can't skip negatively many items
    >>> list(drop('pqr', True))  # OK, since bool is a subclass of int.
    ['q', 'r']
    """
    _validate_drop(n)

    def generate():
        it = iter(iterable)
        collections.deque(itertools.islice(it, n), maxlen=0)
        yield from it

    return generate()


class Drop:
    """
    Iterator to all but the first n elements of an iterable.

    This is like drop, but implemented as a class.

    Please don't call islice in this implementation with more than 2 arguments.

    >>> list(Drop(range(5), 0))
    [0, 1, 2, 3, 4]
    >>> list(Drop(range(5), 1))
    [1, 2, 3, 4]
    >>> list(Drop(range(5), 2))
    [2, 3, 4]
    >>> list(Drop(range(5), 4))
    [4]
    >>> list(Drop(range(5), 5))
    []
    >>> list(Drop(range(5), 6))
    []
    >>> list(Drop(range(5), 1_000_000))
    []
    >>> it = take(Drop(itertools.count(1), 1000), 2)
    >>> next(it)
    1001
    >>> next(it)
    1002
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> Drop(range(5), -1.0)
    Traceback (most recent call last):
      ...
    TypeError: n must be an int
    >>> Drop(range(5), -1)
    Traceback (most recent call last):
      ...
    ValueError: can't skip negatively many items
    >>> list(Drop('pqr', True))  # OK, since bool is a subclass of int.
    ['q', 'r']
    """

    __slots__ = ('_started', '_drop_count', '_iterator')

    def __init__(self, iterable, n):
        _validate_drop(n)
        self._started = False
        self._drop_count = n
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._started:
            self._started = True
            prefix = itertools.islice(self._iterator, self._drop_count)
            collections.deque(prefix, maxlen=0)

        return next(self._iterator)


def last(iterable):
    """
    Return the last element of iterable, or raise IndexError if it is empty.

    >>> last(x for x in ())
    Traceback (most recent call last):
      ...
    IndexError: can't get last item from empty iterable
    >>> last(x for x in (10,))
    10
    >>> last(['foo', 'bar', 'baz', 'quux', 'foobar'])
    'foobar'
    >>> last(iter(range(100_000)))
    99999
    >>> last('I code in all the scary animals in my house including Python')
    'n'
    """
    queue = collections.deque(iterable, 1)
    if queue:
        return queue[0]
    raise IndexError("can't get last item from empty iterable")


def tail(iterable, n):
    """
    Return a tuple of the last n elements of iterable.

    If there are fewer than n elements in iterable, return all of them.

    For an iterable of length L, this should take O(L) time and use
    O(min(L, n)) auxiliary space.

    >>> tail([], 0)
    ()
    >>> tail([], 1)
    ()
    >>> tail((x**2 for x in range(100)), 5)
    (9025, 9216, 9409, 9604, 9801)
    >>> it = iter(range(1000))
    >>> tail(it, 0)
    ()
    >>> list(it)  # Even with n=0, the iterable is iterated through.
    []
    """
    return tuple(collections.deque(iterable, n))


def tail_opt(iterable, n):
    """
    Return a tuple of the last n elements of iterable, by slicing if supported.

    As in tail (above), return all elements if there are fewer than n of them.

    Unlike tail, tail_opt is never required to iterate through all elements,
    even if it cannot use slicing (though usually it will have to).

    >>> tail_opt([], 0)
    ()
    >>> tail_opt([], 1)
    ()
    >>> tail_opt((x**2 for x in range(100)), 5)
    (9025, 9216, 9409, 9604, 9801)
    >>> class MyList(list):
    ...     def __iter__(self):
    ...         print('Iterating.')
    ...         return super().__iter__()
    >>> a = MyList([10, 20, 30, 40])
    >>> tail_opt(a, 6) == tail_opt(a, 5) == tail_opt(a, 4) == (10, 20, 30, 40)
    True
    >>> (tail_opt(a, 3), tail_opt(a, 2), tail_opt(a, 1), tail_opt(a, 0))
    ((20, 30, 40), (30, 40), (40,), ())
    >>> it = itertools.chain(a)  # "Chain" a by itself but don't call iter yet.
    >>> tail_opt(it, 3)
    Iterating.
    (20, 30, 40)
    >>> tail_opt(range(1_000_000_000_000), 5)  # Hopefully this uses slicing!
    (999999999995, 999999999996, 999999999997, 999999999998, 999999999999)
    >>> tail_opt(dict.fromkeys(range(1000)), 3)
    (997, 998, 999)
    >>> sorted(tail_opt({'a', 'b', 'c', 'd', 'e'}, 128))
    ['a', 'b', 'c', 'd', 'e']
    """
    if n == 0:
        return ()
    try:
        return tuple(iterable[-n:])
    except TypeError:
        return tail(iterable, n)


def pick(iterable, index):
    """
    Return the item from the iterable at the index (0-based indexing).

    If index is out of range, raise IndexError.

    It's possible to support negative indices, but raise IndexError instead.

    >>> pick((x for x in ()), 0)
    Traceback (most recent call last):
      ...
    IndexError: index out of range
    >>> pick((x for x in (10,)), -1)
    Traceback (most recent call last):
      ...
    IndexError: negative indices are not supported
    >>> pick((x for x in (10,)), 0)
    10
    >>> pick(range(10_000), 4422)
    4422
    >>> pick(iter(range(10_000)), 4422)
    4422
    """
    if index < 0:
        raise IndexError("negative indices are not supported")

    try:
        return next(drop(iterable, index))
    except StopIteration:
        raise IndexError("index out of range")


def _validate_windowed(n):
    """Raise an appropriate exception if windowed should not accept n."""
    if not isinstance(n, int):
        raise TypeError('n must be an int')
    if n < 0:
        raise ValueError("window width (n) cannot be negative")


def windowed(iterable, n):
    """
    Yield all width-n contiguous subsequences of iterable, in order, as tuples.

    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 0))
    [(), (), (), (), (), ()]
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 1))
    [('Ab',), ('Cd',), ('Efg',), ('Hi',), ('Jk',)]
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 2))
    [('Ab', 'Cd'), ('Cd', 'Efg'), ('Efg', 'Hi'), ('Hi', 'Jk')]
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 3))
    [('Ab', 'Cd', 'Efg'), ('Cd', 'Efg', 'Hi'), ('Efg', 'Hi', 'Jk')]
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 4))
    [('Ab', 'Cd', 'Efg', 'Hi'), ('Cd', 'Efg', 'Hi', 'Jk')]
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 5))
    [('Ab', 'Cd', 'Efg', 'Hi', 'Jk')]
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 6))
    []
    >>> list(windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 7))
    []
    >>> list(itertools.islice(windowed(range(1_000_000_000_000), 3), 4))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    """
    _validate_windowed(n)
    it = iter(iterable)
    queue = collections.deque(itertools.islice(it, n), n)

    if n > len(queue):
        return

    yield tuple(queue)

    for element in it:
        queue.append(element)
        yield tuple(queue)


class Windowed:
    """
    Iterator to all width-n contiguous subsequences of iterable, in order, as
    tuples.

    This is like windowed, but implemented as a class.

    Please implement this without using islice, at least initially.

    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 0))
    [(), (), (), (), (), ()]
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 1))
    [('Ab',), ('Cd',), ('Efg',), ('Hi',), ('Jk',)]
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 2))
    [('Ab', 'Cd'), ('Cd', 'Efg'), ('Efg', 'Hi'), ('Hi', 'Jk')]
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 3))
    [('Ab', 'Cd', 'Efg'), ('Cd', 'Efg', 'Hi'), ('Efg', 'Hi', 'Jk')]
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 4))
    [('Ab', 'Cd', 'Efg', 'Hi'), ('Cd', 'Efg', 'Hi', 'Jk')]
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 5))
    [('Ab', 'Cd', 'Efg', 'Hi', 'Jk')]
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 6))
    []
    >>> list(Windowed(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk']), 7))
    []
    >>> list(itertools.islice(Windowed(range(1_000_000_000_000), 3), 4))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    """

    __slots__ = ('_started', '_queue', '_iterator')

    def __init__(self, iterable, n):
        _validate_windowed(n)
        self._started = False
        self._queue = collections.deque(maxlen=n)
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        if self._started:
            self._queue.append(next(self._iterator))
            return tuple(self._queue)

        while len(self._queue) < self._queue.maxlen:
            self._queue.append(next(self._iterator))
        self._started = True
        return tuple(self._queue)


def windowed_alt(iterable, n):
    """
    Yield all width-n contiguous subsequences of iterable, in order, as tuples.

    This alternative implementation is much shorter than windowed (above),
    because this uses something from the more-itertools library.

    >>> scap = str.capitalize  # To keep the following lines under 80 columns.
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 0))
    [(), (), (), (), (), ()]
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 1))
    [('Ab',), ('Cd',), ('Efg',), ('Hi',), ('Jk',)]
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 2))
    [('Ab', 'Cd'), ('Cd', 'Efg'), ('Efg', 'Hi'), ('Hi', 'Jk')]
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 3))
    [('Ab', 'Cd', 'Efg'), ('Cd', 'Efg', 'Hi'), ('Efg', 'Hi', 'Jk')]
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 4))
    [('Ab', 'Cd', 'Efg', 'Hi'), ('Cd', 'Efg', 'Hi', 'Jk')]
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 5))
    [('Ab', 'Cd', 'Efg', 'Hi', 'Jk')]
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 6))
    []
    >>> list(windowed_alt(map(scap, ['ab', 'cd', 'efg', 'hi', 'jk']), 7))
    []
    >>> list(itertools.islice(windowed_alt(range(1_000_000_000_000), 3), 4))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    """
    return more_itertools.sliding_window(iterable, n)


def my_pairwise(iterable):
    """
    Yield all pairs of consecutive items from iterable, allowing overlap.

    This is like itertools.pairwise(iterable), or windowed(iterable, 2). Don't
    use either of those or collections.deque. You can use anything else though.

    TODO: Implement this any way you like at first, but you should also get it
    working without any loops, comprehensions, try blocks, with statements,
    helper functions (or classes), or calls to anything else in this project.

    >>> list(my_pairwise(range(10)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    >>> [list(my_pairwise(range(n))) for n in range(5)]
    [[], [], [(0, 1)], [(0, 1), (1, 2)], [(0, 1), (1, 2), (2, 3)]]
    >>> list(my_pairwise(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk'])))
    [('Ab', 'Cd'), ('Cd', 'Efg'), ('Efg', 'Hi'), ('Hi', 'Jk')]
    >>> list(itertools.islice(my_pairwise(itertools.count()), 9))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    >>> it = my_pairwise(print(i) for i in range(10))
    >>> next(it)
    0
    1
    (None, None)
    >>> next(it)
    2
    (None, None)
    """
    left, right = itertools.tee(iterable)
    next(right, None)
    yield from zip(left, right)


class Pairwise:
    """
    Iterator to all pairs of consecutive items from iterable, allowing overlap.

    This is like my_pairwise, but implemented as a class. Don't use anything
    from this project or the itertools or collections modules. Don't use any
    builtins other than iter and next.

    >>> list(Pairwise(range(10)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    >>> [list(Pairwise(range(n))) for n in range(5)]
    [[], [], [(0, 1)], [(0, 1), (1, 2)], [(0, 1), (1, 2), (2, 3)]]
    >>> list(Pairwise(map(str.capitalize, ['ab', 'cd', 'efg', 'hi', 'jk'])))
    [('Ab', 'Cd'), ('Cd', 'Efg'), ('Efg', 'Hi'), ('Hi', 'Jk')]
    >>> list(itertools.islice(Pairwise(itertools.count()), 9))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    >>> it = Pairwise(print(i) for i in range(10))
    >>> next(it)
    0
    1
    (None, None)
    >>> next(it)
    2
    (None, None)
    """

    __slots__ = ('_iterator', '_started', '_pre')

    def __init__(self, iterable):
        self._iterator = iter(iterable)
        self._started = False
        self._pre = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self._started:
            self._pre = next(self._iterator)
            self._started = True

        cur = next(self._iterator)
        pair = (self._pre, cur)
        self._pre = cur
        return pair


def map_one(func, iterable):
    """
    Map values from the given iterable through the unary function func.

    This is like the built-in map, except it doesn't accept multiple iterables.

    That is, map accepts an n-ary function and n iterable arguments, but
    map_one requires a unary function and exactly one iterable argument.

    >>> list(map_one(lambda x: x**2, range(1, 11)))
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    >>> next(map_one(lambda x: x**2, range(0)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(map_one(len, ['foobar', (10, 20), range(1000)]))
    [6, 2, 1000]
    >>> list(map_one(lambda x: x + 1, (x**2 for x in range(1, 6))))
    [2, 5, 10, 17, 26]
    """
    return (func(element) for element in iterable)


def map_one_alt(func, iterable):
    """
    Map values from the given iterable through the unary function func.

    This behaves the same as map_one (above) but is implemented differently.
    One of the implementations uses a comprehension and the other does not.

    >>> list(map_one_alt(lambda x: x**2, range(1, 11)))
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    >>> next(map_one_alt(lambda x: x**2, range(0)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(map_one_alt(len, ['foobar', (10, 20), range(1000)]))
    [6, 2, 1000]
    >>> list(map_one_alt(lambda x: x + 1, (x**2 for x in range(1, 6))))
    [2, 5, 10, 17, 26]
    """
    for element in iterable:
        yield func(element)


class MapOne:
    """
    Map an iterable through a unary function.

    This is like the built-in map, except it doesn't accept multiple iterables.

    This is like map_one and map_one_alt, but implemented as a class.

    >>> list(MapOne(lambda x: x**2, range(1, 11)))
    [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    >>> next(MapOne(lambda x: x**2, range(0)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(MapOne(len, ['foobar', (10, 20), range(1000)]))
    [6, 2, 1000]
    >>> list(MapOne(lambda x: x + 1, (x**2 for x in range(1, 6))))
    [2, 5, 10, 17, 26]
    """

    __slots__ = ('_func', '_iterator')

    def __init__(self, func, iterable):
        self._func = func
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        return self._func(next(self._iterator))


def my_filter(predicate, iterable):
    """
    Return an iterator of the values in an iterable that satisfy the predicate.

    If the predicate is None instead of a function, the iterator will yield the
    values of the iterable that are truthy.

    This is the same behavior as the builtin filter.

    >>> next(my_filter(lambda n: n < 0, (0, 1, 2)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(my_filter(lambda x: len(x) == 3, ['ham', 'spam', 'foo', 'eggs']))
    ['ham', 'foo']
    >>> mixed = ('p', 'xy', [3], (1, 2, 3), 'c')
    >>> list(my_filter(None, (a[1:] for a in mixed)))
    ['y', (2, 3)]
    >>> list(my_filter(None, ['hello', 'glorious', 'world']))
    ['hello', 'glorious', 'world']
    """
    if predicate is None:
        predicate = identity_function

    return (element for element in iterable if predicate(element))


def my_filter_alt(predicate, iterable):
    """
    Return an iterator of the values in an iterable that satisfy the predicate.

    If the predicate is None instead of a function, the iterator will yield the
    values of the iterable that are truthy.

    This behaves the same as my_filter (above) and the builtin filter, but its
    implementation differs from that of my_filter. One of the implementations
    uses a comprehension, and the other does not.

    >>> next(my_filter_alt(lambda n: n < 0, (0, 1, 2)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> foods = ['ham', 'spam', 'foo', 'eggs']
    >>> list(my_filter_alt(lambda x: len(x) == 3, foods))
    ['ham', 'foo']
    >>> mixed = ('p', 'xy', [3], (1, 2, 3), 'c')
    >>> list(my_filter_alt(None, (a[1:] for a in mixed)))
    ['y', (2, 3)]
    >>> list(my_filter_alt(None, ['hello', 'glorious', 'world']))
    ['hello', 'glorious', 'world']
    """
    if predicate is None:
        predicate = identity_function

    for element in iterable:
        if predicate(element):
            yield element


class Filter:
    """
    Iterator of the values in an iterable that satisfy a predicate.

    If the predicate is None instead of a function, the this yields the values
    of the iterable that are truthy.

    This is like my_filter and my_filter_alt, but implemented as a class.

    >>> next(Filter(lambda n: n < 0, (0, 1, 2)))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(Filter(lambda x: len(x) == 3, ['ham', 'spam', 'foo', 'eggs']))
    ['ham', 'foo']
    >>> mixed = ('p', 'xy', [3], (1, 2, 3), 'c')
    >>> list(Filter(None, (a[1:] for a in mixed)))
    ['y', (2, 3)]
    >>> list(Filter(None, ['hello', 'glorious', 'world']))
    ['hello', 'glorious', 'world']
    """

    __slots__ = ('_predicate', '_iterator')

    def __init__(self, predicate, iterable):
        self._predicate = ((lambda x: x) if predicate is None else predicate)
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        for item in self._iterator:
            if self._predicate(item):
                return item

        raise StopIteration()


def length_of(iterable):
    """
    Count the number of items in an iterable, which need not support len.

    >>> length_of(range(1000))
    1000
    >>> length_of(iter(range(1000)))
    1000
    >>> length_of(x for x in range(1000))
    1000
    >>> length_of(x for x in ())
    0
    >>> length_of(x for x in ['ham', 'spam', 'foo', 'eggs', ''] if len(x) == 3)
    2
    >>> length_of({object() for _ in range(100_000)})
    100000
    """
    return sum(1 for _ in iterable)


def length_of_opt(iterable):
    """
    Count the number of items in any iterable, but use len if it is supported.

    This may be viewed as an optimized implementation of length_of.

    >>> length_of_opt(range(1000))
    1000
    >>> length_of_opt(iter(range(1000)))
    1000
    >>> length_of_opt(x for x in range(1000))
    1000
    >>> length_of_opt(x for x in ())
    0
    >>> length_of_opt(x for x in ['ham', 'sp', 'foo', 'eg', ''] if len(x) == 3)
    2
    >>> length_of_opt({object() for _ in range(100_000)})
    100000
    >>> length_of_opt(range(2_000_000_000))
    2000000000
    >>> set(length_of_opt(range(2_000_000_000)) for _ in range(100_000))
    {2000000000}
    """
    try:
        return len(iterable)
    except TypeError:
        return sum(1 for _ in iterable)


def how_many(predicate, iterable):
    """
    Count the number of items in an iterable that satisfy a predicate.

    If predicate is None instead of a unary function, count truthy items.

    >>> how_many(lambda n: n % 3 == 0, range(1, 12))
    3
    >>> how_many(lambda n: n % 3 == 0, range(1, 13))
    4
    >>> how_many(lambda s: len(s) == 4,
    ...          (t * 2 for t in ['a', 'bc', 'de', 'f', 'ghi', 'jk']))
    3
    >>> how_many(None, iter([(), [], '', 'a', {}, set(), [0], None]))
    2
    >>> how_many(lambda _: True, [0, 1] * 100_000)
    200000
    >>> o = object()
    >>> how_many(lambda x: x == o, (object() for _ in range(100_000)))
    0
    """
    return sum(1 for _ in filter(predicate, iterable))


def invert(dictionary):
    """
    Given an injective (that is, one-to-one) dictionary, return its inverse.

    When a dictionary never maps unequal keys to equal values, it is possible
    to produce an inverse of it: a dictionary that maps the values back to the
    keys.

    This also needs the dictionary's values (not just its keys) to be hashable.

    >>> invert({})
    {}
    >>> invert({'a': 10, 'b': 20, 'cd': 30, 'efg': 40})
    {10: 'a', 20: 'b', 30: 'cd', 40: 'efg'}
    >>> r = range(100_000)
    >>> invert({x: x**2 for x in r}) == {x**2: x for x in r}
    True
    >>> invert({x: x for x in r}) == {x: x for x in r}
    True
    >>> import random
    >>> a = list(range(-50_000, 50_001))
    >>> random.shuffle(a)
    >>> b = [x**3 for x in a]
    >>> random.shuffle(b)
    >>> d = {k: v for k, v in zip(a, b)}
    >>> invert(d) == d
    False
    >>> invert(invert(d)) == d
    True

    If a non-injective dictionary is passed, the last value associated with the
    key will be assigned because the first and intermediate values will be
    overwritten.

    >>> invert({'a': 1, 'b': 1, 'c': 1})
    {1: 'c'}
    """
    return {value: key for key, value in dictionary.items()}


def invert_alt(dictionary):
    """
    Given an injective (that is, one-to-one) dictionary, return its inverse.

    When a dictionary never maps unequal keys to equal values, it is possible
    to produce an inverse of it: a dictionary that maps the values back to the
    keys.

    This also needs the dictionary's values (not just its keys) to be hashable.

    This alternative implementation behaves the same as invert (above) but does
    not use a comprehension.

    >>> invert_alt({})
    {}
    >>> invert_alt({'a': 10, 'b': 20, 'cd': 30, 'efg': 40})
    {10: 'a', 20: 'b', 30: 'cd', 40: 'efg'}
    >>> r = range(100_000)
    >>> invert_alt({x: x**2 for x in r}) == {x**2: x for x in r}
    True
    >>> invert_alt({x: x for x in r}) == {x: x for x in r}
    True
    >>> import random
    >>> a = list(range(-50_000, 50_001))
    >>> random.shuffle(a)
    >>> b = [x**3 for x in a]
    >>> random.shuffle(b)
    >>> d = {k: v for k, v in zip(a, b)}
    >>> invert_alt(d) == d
    False
    >>> invert_alt(invert_alt(d)) == d
    True

    If a non-injective dictionary is passed, the last value associated with the
    key will be assigned because the first and intermediate values will be
    overwritten.

    >>> invert_alt({'a': 1, 'b': 1, 'c': 1})
    {1: 'c'}
    """
    inverse = {}
    for key, value in dictionary.items():
        inverse[value] = key
    return inverse


def distinct_simple(iterable):
    """
    Yield only first occurrences of equal items.

    It is permitted to assume all values of the input iterable are hashable.

    >>> next(distinct_simple([]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(distinct_simple({3}))
    [3]
    >>> list(distinct_simple(('foo', 'foo')))
    ['foo']
    >>> list(distinct_simple(x**2 for x in range(-3, 6)))
    [9, 4, 1, 0, 16, 25]
    >>> it = distinct_simple([2, 1, 2, 4, 1, 7] * 100_000)
    >>> next(it)
    2
    >>> list(it)
    [1, 4, 7]
    """
    return distinct(iterable)


class DistinctSimple:
    """
    Iterator to only first occurrences of equal items.

    This is like distinct_simple (above), but implemented as a class. So it is
    permitted to assume all values of the input iterable are hashable.

    >>> next(DistinctSimple([]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(DistinctSimple({3}))
    [3]
    >>> list(DistinctSimple(('foo', 'foo')))
    ['foo']
    >>> list(DistinctSimple(x**2 for x in range(-3, 6)))
    [9, 4, 1, 0, 16, 25]
    >>> it = DistinctSimple([2, 1, 2, 4, 1, 7] * 100_000)
    >>> next(it)
    2
    >>> list(it)
    [1, 4, 7]
    """

    __slots__ = ('_history', '_iterator')

    def __init__(self, iterable):
        self._history = set()
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        for item in self._iterator:
            if item not in self._history:
                self._history.add(item)
                return item

        raise StopIteration()


def distinct(iterable, *, key=None):
    """
    Yield only first occurrences of values whose associated keys are equal.

    The key parameter is a unary function serving as a key selector. When
    calling this function with a value from the iterable gives the same result
    as calling it with an earlier value from the iterable, don't yield the new
    value.

    The key parameter may also be None instead of a function, in which case
    values in the iterable are considered to be their own keys. Another way of
    saying this is that calling distinct without passing a key selector has the
    same behavior as calling distinct_simple.

    It is permitted to assume the key selector returns only hashable objects,
    and that it is consistent, i.e., when x is y, key(x) == key(y).

    Assume distinct_simple's implementation may change in the future to simply
    forward its argument to distinct (so this shouldn't call distinct_simple).

    >>> next(distinct([]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(distinct({3}))
    [3]
    >>> list(distinct(('foo', 'foo')))
    ['foo']
    >>> list(distinct(x**2 for x in range(-3, 6)))
    [9, 4, 1, 0, 16, 25]
    >>> it = distinct([2, 1, 2, 4, 1, 7] * 100_000)
    >>> next(it)
    2
    >>> list(it)
    [1, 4, 7]

    >>> list(distinct(('foo', 'bar', 'foobar', 'baz', 'quux', 'wq'), key=len))
    ['foo', 'foobar', 'quux', 'wq']
    >>> list(distinct(range(-3, 6), key=lambda x: x**2))
    [-3, -2, -1, 0, 4, 5]
    >>> list(distinct([[1, 2, 3], [1, 3, 2], [1, 2, 3], [2, 1, 3]], key=tuple))
    [[1, 2, 3], [1, 3, 2], [2, 1, 3]]
    >>> middle = [[], []] * 100_000
    >>> list(distinct([3, *middle, 4], key=id))
    [3, [], [], 4]
    """
    if key is None:
        key = identity_function

    observed = set()

    for element in iterable:
        result = key(element)
        if result not in observed:
            observed.add(result)
            yield element


class Distinct:
    """
    Iterator to only first occurrences of values whose associated keys are
    equal.

    This is like distinct (above), but implemented as a class. The meaning and
    restrictions on arguments used to construct a Distinct object are the same
    as those documented for the arguments used to call the distinct function.

    >>> next(Distinct([]))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(Distinct({3}))
    [3]
    >>> list(Distinct(('foo', 'foo')))
    ['foo']
    >>> list(Distinct(x**2 for x in range(-3, 6)))
    [9, 4, 1, 0, 16, 25]
    >>> it = Distinct([2, 1, 2, 4, 1, 7] * 100_000)
    >>> next(it)
    2
    >>> list(it)
    [1, 4, 7]

    >>> list(Distinct(('foo', 'bar', 'foobar', 'baz', 'quux', 'wq'), key=len))
    ['foo', 'foobar', 'quux', 'wq']
    >>> list(Distinct(range(-3, 6), key=lambda x: x**2))
    [-3, -2, -1, 0, 4, 5]
    >>> list(Distinct([[1, 2, 3], [1, 3, 2], [1, 2, 3], [2, 1, 3]], key=tuple))
    [[1, 2, 3], [1, 3, 2], [2, 1, 3]]
    >>> middle = [[], []] * 100_000
    >>> list(Distinct([3, *middle, 4], key=id))
    [3, [], [], 4]
    """

    __slots__ = ('_history', '_key', '_iterator')

    def __init__(self, iterable, *, key=None):
        self._history = set()
        self._key = ((lambda x: x) if key is None else key)
        self._iterator = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        for item in self._iterator:
            mapped_key = self._key(item)
            if mapped_key not in self._history:
                self._history.add(mapped_key)
                return item

        raise StopIteration()


def distinct_dicts_by_single_key_monolithic(dicts, subject_key):
    """
    Yield dictionaries from dicts that differ from each previously seen
    dictionary in their treatment of the subject key.

    dicts is an iterable of dictionaries whose values (not just their keys) are
    hashable.

    subject_key (which I call the "subject key") is some hashable object.

    Consider two dictionaries to agree on the subject key if they cannot be
    distinguished by subscripting with it. That is, dictionaries d1 and d2
    agree on the subject key when either d1 and d2 both have subject_key as a
    key and map it to the same value, or neither d1 nor d2 has it as a key.

    Stated in those terms, yield each dictionary in dicts that does not agree
    on the subject key with any preceding dictionary in dicts.

    This implementation is self-contained. It does not use distinct (above).
    See also distinct_dicts_by_single_key below.

    >>> next(distinct_dicts_by_single_key_monolithic([], 'p'))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> d1 = {'p': 'x', 'q': 'y', 'r': 'z'}
    >>> d2 = {'q': 'y', 'r': 'z', 's': 'w'}
    >>> d3 = {'o': 'z', 'p': 'y', 'q': 'u'}
    >>> d4 = {'o': 'z', 'p': 'x', 'q': 'x', 'r': 'w'}
    >>> ds = [d1, d2, d3, d4]
    >>> list(distinct_dicts_by_single_key_monolithic(ds, 'o')) == [d1, d3]
    True
    >>> list(distinct_dicts_by_single_key_monolithic(ds, 'p')) == [d1, d2, d3]
    True
    >>> list(distinct_dicts_by_single_key_monolithic(ds, 'q')) == [d1, d3, d4]
    True
    >>> list(distinct_dicts_by_single_key_monolithic(ds, 'r')) == [d1, d3, d4]
    True
    >>> list(distinct_dicts_by_single_key_monolithic(ds, 's')) == [d1, d2]
    True
    >>> list(distinct_dicts_by_single_key_monolithic(iter(ds), 's')
    ... ) == [d1, d2]
    True
    >>> it = distinct_dicts_by_single_key_monolithic(ds, 't')
    >>> next(it)
    {'p': 'x', 'q': 'y', 'r': 'z'}
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> d1['p'] = d4['p'] = d4['q'] = object()              # Change 'x'.
    >>> d1['q'] = d2['q'] = d3['p'] = None                  # Change 'y'.
    >>> d1['r'] = d2['r'] = d3['o'] = d4['o'] = object()    # Change 'z'.
    >>> def f(sk): return list(distinct_dicts_by_single_key_monolithic(ds, sk))
    >>> [f(sk) for sk in ('o', 'p', 'q', 'r', 's', 't')] == [
    ...     [d1, d3], [d1, d2, d3], [d1, d3, d4], [d1, d3, d4], [d1, d2], [d1]]
    True
    """
    history = set()
    got_missing = False
    for d in dicts:
        if subject_key in d:
            if d[subject_key] not in history:
                history.add(d[subject_key])
                yield d
        elif not got_missing:
            got_missing = True
            yield d


def distinct_dicts_by_single_key_alt(dicts, subject_key):
    """
    Yield dictionaries from dicts that differ from each previously seen
    dictionary in their treatment of the subject key.

    dicts is an iterable of dictionaries whose values (not just their keys) are
    hashable.

    subject_key (which I call the "subject key") is some hashable object.

    Consider two dictionaries to agree on the subject key if they cannot be
    distinguished by subscripting with it. That is, dictionaries d1 and d2
    agree on the subject key when either d1 and d2 both have subject_key as a
    key and map it to the same value, or neither d1 nor d2 has it as a key.

    Stated in those terms, yield each dictionary in dicts that does not agree
    on the subject key with any preceding dictionary in dicts.

    This implementation uses distinct (defined above) and is thus much shorter
    than distinct_dicts_by_single_key_monolithic (defined immediately above).
    But it is still longer than distinct_dicts_by_single_key (defined below).

    >>> next(distinct_dicts_by_single_key_alt([], 'p'))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> d1 = {'p': 'x', 'q': 'y', 'r': 'z'}
    >>> d2 = {'q': 'y', 'r': 'z', 's': 'w'}
    >>> d3 = {'o': 'z', 'p': 'y', 'q': 'u'}
    >>> d4 = {'o': 'z', 'p': 'x', 'q': 'x', 'r': 'w'}
    >>> ds = [d1, d2, d3, d4]
    >>> list(distinct_dicts_by_single_key_alt(ds, 'o')) == [d1, d3]
    True
    >>> list(distinct_dicts_by_single_key_alt(ds, 'p')) == [d1, d2, d3]
    True
    >>> list(distinct_dicts_by_single_key_alt(ds, 'q')) == [d1, d3, d4]
    True
    >>> list(distinct_dicts_by_single_key_alt(ds, 'r')) == [d1, d3, d4]
    True
    >>> list(distinct_dicts_by_single_key_alt(ds, 's')) == [d1, d2]
    True
    >>> list(distinct_dicts_by_single_key_alt(iter(ds), 's')) == [d1, d2]
    True
    >>> it = distinct_dicts_by_single_key_alt(ds, 't')
    >>> next(it)
    {'p': 'x', 'q': 'y', 'r': 'z'}
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> d1['p'] = d4['p'] = d4['q'] = object()              # Change 'x'.
    >>> d1['q'] = d2['q'] = d3['p'] = None                  # Change 'y'.
    >>> d1['r'] = d2['r'] = d3['o'] = d4['o'] = object()    # Change 'z'.
    >>> def f(sk): return list(distinct_dicts_by_single_key_alt(ds, sk))
    >>> [f(sk) for sk in ('o', 'p', 'q', 'r', 's', 't')] == [
    ...     [d1, d3], [d1, d2, d3], [d1, d3, d4], [d1, d3, d4], [d1, d2], [d1]]
    True
    """
    distinct_object = object()
    return distinct(dicts, key=lambda d: d.get(subject_key, distinct_object))


def distinct_dicts_by_single_key(dicts, subject_key):
    """
    Yield dictionaries from dicts that differ from each previously seen
    dictionary in their treatment of the subject key.

    dicts is an iterable of dictionaries whose values (not just their keys) are
    hashable.

    subject_key (which I call the "subject key") is some hashable object.

    Consider two dictionaries to agree on the subject key if they cannot be
    distinguished by subscripting with it. That is, dictionaries d1 and d2
    agree on the subject key when either d1 and d2 both have subject_key as a
    key and map it to the same value, or neither d1 nor d2 has it as a key.

    Stated in those terms, yield each dictionary in dicts that does not agree
    on the subject key with any preceding dictionary in dicts.

    This implementation is the shortest. It uses distinct_dicts_by_keys
    (below).

    >>> next(distinct_dicts_by_single_key([], 'p'))
    Traceback (most recent call last):
      ...
    StopIteration
    >>> d1 = {'p': 'x', 'q': 'y', 'r': 'z'}
    >>> d2 = {'q': 'y', 'r': 'z', 's': 'w'}
    >>> d3 = {'o': 'z', 'p': 'y', 'q': 'u'}
    >>> d4 = {'o': 'z', 'p': 'x', 'q': 'x', 'r': 'w'}
    >>> ds = [d1, d2, d3, d4]
    >>> list(distinct_dicts_by_single_key(ds, 'o')) == [d1, d3]
    True
    >>> list(distinct_dicts_by_single_key(ds, 'p')) == [d1, d2, d3]
    True
    >>> list(distinct_dicts_by_single_key(ds, 'q')) == [d1, d3, d4]
    True
    >>> list(distinct_dicts_by_single_key(ds, 'r')) == [d1, d3, d4]
    True
    >>> list(distinct_dicts_by_single_key(ds, 's')) == [d1, d2]
    True
    >>> list(distinct_dicts_by_single_key(iter(ds), 's')) == [d1, d2]
    True
    >>> it = distinct_dicts_by_single_key(ds, 't')
    >>> next(it)
    {'p': 'x', 'q': 'y', 'r': 'z'}
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> d1['p'] = d4['p'] = d4['q'] = object()              # Change 'x'.
    >>> d1['q'] = d2['q'] = d3['p'] = None                  # Change 'y'.
    >>> d1['r'] = d2['r'] = d3['o'] = d4['o'] = object()    # Change 'z'.
    >>> def f(sk): return list(distinct_dicts_by_single_key(ds, sk))
    >>> [f(sk) for sk in ('o', 'p', 'q', 'r', 's', 't')] == [
    ...     [d1, d3], [d1, d2, d3], [d1, d3, d4], [d1, d3, d4], [d1, d2], [d1]]
    True
    """
    return distinct_dicts_by_keys(dicts, (subject_key,))


def distinct_dicts_by_keys(dicts, subject_keys):
    """
    Yield dictionaries from dicts that differ from each previously seen
    dictionary in their treatment of (at least one of) the subject keys.

    dicts is an iterable of dictionaries whose values (not just their keys) are
    hashable.

    subject_keys ("the subject keys") is an iterable of hashable objects.

    Consider two dictionaries to agree on the subject keys if the dictionaries
    cannot be distinguished by subscripting with any object in subject_keys.
    That is, dictionaries d1 and d2 agree on the subject keys when, for each k
    in subject_keys, either d1 and d2 both have k as a key and map it to the
    same value, or neither d1 nor d2 has k as a key.

    For example, {'a': 1, 'b': 2, 'c': 3} and {'a': 1, 'b': 1, 'c': 3, 'd': 4}
    agree on ('a', 'c'), disagree on ('a', 'c', 'd'), agree on ('a', 'c', 'e'),
    disagree on ('b',), and agree on ().

    Stated in those terms, yield each dictionary in dicts that does not agree
    on the subject keys with any preceding dictionary in dicts.

    The number of subject keys is expected to be small compared to the number
    and size of the dicts. Assume there will often be millions of dictionaries,
    most of which have millions of key-value entries, but there will only be
    hundreds of subject keys.

    >>> ds1 = [{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5},
    ...        {'e': 6, 'd': 4, 'c': 7, 'b': 2, 'a': 8},
    ...        {'a': 1, 'b': 2, 'c': 3, 'e': 5}]
    >>> it = distinct_dicts_by_keys(ds1, ['d', 'f'])
    >>> next(it)
    {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    >>> next(it)
    {'a': 1, 'b': 2, 'c': 3, 'e': 5}
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> ds2 = [{1.2: 'j', 7.1: 't', 3.6: 'u', 4.4: 'k', 9.0: 'n', -2.7: 'q'},
    ...        {1.2: 'j', 7.1: 'u', 3.6: 'v', 4.4: 'j', 9.0: 'o', -2.7: 't'},
    ...        {1.2: 'j', 7.1: 'v', 3.6: 'w', 4.4: 'k', 9.0: 'p', -2.7: 'u'},
    ...        {1.2: 'l', 7.1: 'v', 3.6: 'x', 4.4: 'l', 9.0: 'q', -2.7: 'v'},
    ...        {1.2: 'j', 7.1: 'w', 3.6: 'x', 4.4: 'k', 9.0: 'r', -2.7: 't'},
    ...        {7.1: 'x', 3.6: 'y', 4.4: 'l', 9.0: 's', -2.7: 't'}]
    >>> it = distinct_dicts_by_keys(ds2, (x for x in (1.2, 5.8, 4.4)))
    >>> for d in it: print(d)
    {1.2: 'j', 7.1: 't', 3.6: 'u', 4.4: 'k', 9.0: 'n', -2.7: 'q'}
    {1.2: 'j', 7.1: 'u', 3.6: 'v', 4.4: 'j', 9.0: 'o', -2.7: 't'}
    {1.2: 'l', 7.1: 'v', 3.6: 'x', 4.4: 'l', 9.0: 'q', -2.7: 'v'}
    {7.1: 'x', 3.6: 'y', 4.4: 'l', 9.0: 's', -2.7: 't'}
    >>> list(it)  # Show that it was an iterator (and thus exhausted).
    []
    >>> list(distinct_dicts_by_keys(ds2, ()))  # Make disagreement impossible.
    [{1.2: 'j', 7.1: 't', 3.6: 'u', 4.4: 'k', 9.0: 'n', -2.7: 'q'}]
    >>> x = object()
    >>> y = object()
    >>> ds2 = [{'p': x, 'q': y, 'r': object()} for _ in range(2)]
    >>> sum(1 for _ in distinct_dicts_by_keys(ds2, ('p', 'q')))
    1
    >>> sum(1 for _ in distinct_dicts_by_keys(ds2, ('q', 'r')))
    2
    >>> cipher = {normal: object() for normal in range(1, 9)}
    >>> cipher[4] = None
    >>> decipher = {weird: normal for normal, weird in cipher.items()}
    >>> ds3 = [{k: cipher[v] for k, v in d.items()} for d in ds1]
    >>> for d in distinct_dicts_by_keys(ds3, ['d', 'f']):
    ...     print({k: decipher[weird] for k, weird in d.items()})
    {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    {'a': 1, 'b': 2, 'c': 3, 'e': 5}
    >>> list(distinct_dicts_by_keys([{'a': 1}, {'b': 1}], ('a', 'b')))
    [{'a': 1}, {'b': 1}]
    """
    my_keys = list(subject_keys)
    o = object()

    def keyfunction(d):
        return tuple(d.get(key, o) for key in my_keys)

    return distinct(dicts, key=keyfunction)


class DistinctDictsByKeys(Distinct):
    """
    Iterator to dictionaries that differ from each previously seen dictionary
    in their treatment of (at least one of) the subject keys.

    This is the class version distinct_dicts_by_keys (above). See its docstring
    for explanations of phrases "differ from ... treatment ... subject keys."

    Arguments to the distinct_dict_by_keys correspond in meaning, and have the
    same restrictions, as argument used to construct a DistinctDictsByKeys
    object.

    Do not call any top-level functions defined in this module. In particular,
    do not call distinct. However, feel free to use (and call) classes defined
    above. Just as distinct_dict_by_keys uses distinct, this class should
    probably make use of Distinct, greatly simplifying the solution.

    NOTE: It's part of the exercise that this must be a class. But really, it
    shouldn't be one, and having it be one is a bad design. The requirements
    don't contain anything a class does better than a function. If what you
    have already is the Distinct class, you can use that in a function, the
    exact same way the distinct_dict_by_keys function uses the distinct
    function. So the technique used here is easy to overuse. But it is
    occasionally useful. [FIXME: Give an example of when it would be useful.]

    >>> ds1 = [{'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5},
    ...        {'e': 6, 'd': 4, 'c': 7, 'b': 2, 'a': 8},
    ...        {'a': 1, 'b': 2, 'c': 3, 'e': 5}]
    >>> it = DistinctDictsByKeys(ds1, ['d', 'f'])
    >>> next(it)
    {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    >>> next(it)
    {'a': 1, 'b': 2, 'c': 3, 'e': 5}
    >>> next(it)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> ds2 = [{1.2: 'j', 7.1: 't', 3.6: 'u', 4.4: 'k', 9.0: 'n', -2.7: 'q'},
    ...        {1.2: 'j', 7.1: 'u', 3.6: 'v', 4.4: 'j', 9.0: 'o', -2.7: 't'},
    ...        {1.2: 'j', 7.1: 'v', 3.6: 'w', 4.4: 'k', 9.0: 'p', -2.7: 'u'},
    ...        {1.2: 'l', 7.1: 'v', 3.6: 'x', 4.4: 'l', 9.0: 'q', -2.7: 'v'},
    ...        {1.2: 'j', 7.1: 'w', 3.6: 'x', 4.4: 'k', 9.0: 'r', -2.7: 't'},
    ...        {7.1: 'x', 3.6: 'y', 4.4: 'l', 9.0: 's', -2.7: 't'}]
    >>> it = DistinctDictsByKeys(ds2, (x for x in (1.2, 5.8, 4.4)))
    >>> for d in it: print(d)
    {1.2: 'j', 7.1: 't', 3.6: 'u', 4.4: 'k', 9.0: 'n', -2.7: 'q'}
    {1.2: 'j', 7.1: 'u', 3.6: 'v', 4.4: 'j', 9.0: 'o', -2.7: 't'}
    {1.2: 'l', 7.1: 'v', 3.6: 'x', 4.4: 'l', 9.0: 'q', -2.7: 'v'}
    {7.1: 'x', 3.6: 'y', 4.4: 'l', 9.0: 's', -2.7: 't'}
    >>> list(it)  # Show that it was an iterator (and thus exhausted).
    []
    >>> list(DistinctDictsByKeys(ds2, ()))  # Make disagreement impossible.
    [{1.2: 'j', 7.1: 't', 3.6: 'u', 4.4: 'k', 9.0: 'n', -2.7: 'q'}]
    >>> x = object()
    >>> y = object()
    >>> ds2 = [{'p': x, 'q': y, 'r': object()} for _ in range(2)]
    >>> sum(1 for _ in DistinctDictsByKeys(ds2, ('p', 'q')))
    1
    >>> sum(1 for _ in DistinctDictsByKeys(ds2, ('q', 'r')))
    2
    >>> cipher = {normal: object() for normal in range(1, 9)}
    >>> cipher[4] = None
    >>> decipher = {weird: normal for normal, weird in cipher.items()}
    >>> ds3 = [{k: cipher[v] for k, v in d.items()} for d in ds1]
    >>> for d in DistinctDictsByKeys(ds3, ['d', 'f']):
    ...     print({k: decipher[weird] for k, weird in d.items()})
    {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    {'a': 1, 'b': 2, 'c': 3, 'e': 5}
    >>> list(DistinctDictsByKeys([{'a': 1}, {'b': 1}], ('a', 'b')))
    [{'a': 1}, {'b': 1}]
    """

    __slots__ = ()

    def __init__(self, dicts, subject_keys):
        not_there = object()
        my_keys = tuple(subject_keys)

        def key(dictionary):
            return tuple(dictionary.get(k, not_there) for k in my_keys)

        super().__init__(dicts, key=key)


__all__ = [thing.__name__ for thing in (
    my_enumerate,
    my_enumerate_alt,
    Enumerate,
    print_enumerated,
    print_enumerated_alt,
    my_any,
    my_any_alt,
    my_all,
    my_all_alt,
    zip_two,
    ZipTwo,
    my_zip,
    Zip,
    print_zipped,
    take_good,
    take,
    Take,
    drop_good,
    drop,
    Drop,
    last,
    tail,
    tail_opt,
    pick,
    windowed,
    Windowed,
    windowed_alt,
    my_pairwise,
    Pairwise,
    map_one,
    map_one_alt,
    MapOne,
    my_filter,
    my_filter_alt,
    Filter,
    length_of,
    length_of_opt,
    how_many,
    invert,
    invert_alt,
    distinct_simple,
    DistinctSimple,
    distinct,
    Distinct,
    distinct_dicts_by_single_key_monolithic,
    distinct_dicts_by_single_key_alt,
    distinct_dicts_by_single_key,
    distinct_dicts_by_keys,
    DistinctDictsByKeys,
)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
