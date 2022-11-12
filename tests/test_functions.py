#!/usr/bin/env python

"""Tests for the functions in functions.py."""

import collections
from collections.abc import Iterator
import contextlib
import functools
import inspect
import io
import itertools
import os
import sys
import unittest
import unittest.mock
import weakref

from parameterized import parameterized, parameterized_class

from algoviz import fibonacci, functions, recursion, testing

_original_count_tree_nodes = functions.count_tree_nodes


class _IterableWithGeneratorIterator:
    """A non-iterator iterable whose iterator is a generator."""

    __slots__ = ('_start',)

    def __init__(self, start=0):
        self._start = start

    def __repr__(self):
        return f'{type(self).__name__}({self._start!r})'

    def __iter__(self):
        while True:
            yield self._start
            self._start += 1


class _CloseableNonGeneratorIterator:
    """An iterator that isn't a generator but has a similar close method."""

    __slots__ = ('_next_result',)

    def __init__(self, start=0):
        self._next_result = start

    def __repr__(self):
        return f'{type(self).__name__}({self._next_result!r})'

    def __iter__(self):
        return self

    def __next__(self):
        if self._next_result is None:
            raise StopIteration
        result = self._next_result
        self._next_result += 1
        return result

    def close(self):
        self._next_result = None


class _IterableWithCloseableNonGeneratorIterator:
    """A non-iterator iterable whose iterator is a closeable non-generator."""

    __slots__ = ('_start',)

    def __init__(self, start=0):
        self._start = start

    def __repr__(self):
        return f'{type(self).__name__}({self._start!r})'

    def __iter__(self):
        return _CloseableNonGeneratorIterator(self._start)


class _NonCloseableIterator:
    """An iterator that isn't a generator and doesn't have a close method."""

    __slots__ = ('_next_result',)

    def __init__(self, start=0):
        self._next_result = start

    def __repr__(self):
        return f'{type(self).__name__}({self._next_result!r})'

    def __iter__(self):
        return self

    def __next__(self):
        result = self._next_result
        self._next_result += 1
        return result


class _CloseableIterableWithNonCloseableIterator:
    """
    A non-iterator iterable with a close method and a non-closeable iterator.
    """

    __slots__ = ('_start',)

    def __init__(self, start=0):
        self._start = start

    def __repr__(self):
        return f'{type(self).__name__}({self._start!r})'

    def __iter__(self):
        return _NonCloseableIterator(self._start)

    def close(self):
        """Raise an AssertionError, since our tests should not call this."""
        raise AssertionError('attempt to close the iterable itself')


@functools.cache
def _fib5k():
    """Return a list of the first 5000 Fibonacci numbers, read from a file."""
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fib5k.txt')
    with open(path, encoding='utf-8') as file:
        return list(map(int, file))


class _NamedImplementationTestCase(unittest.TestCase):
    """
    Base class to test entities in the functions module by their names.

    The recommended use is to inherit from this class and assign an unqualified
    attribute name (most often a function name) to the implementation_name
    class attribute by using the @parameterized.parameterized_class decorator.
    """

    @property
    def implementation(self):
        """The function being tested."""
        return getattr(functions, self.implementation_name)


@parameterized_class(('implementation_name',), [
    ('make_counter',),
    ('make_counter_alt',),
])
class TestMakeCounter(_NamedImplementationTestCase):
    """Tests for the make_counter and make_counter_alt functions."""

    def test_starts_at_zero_with_no_start_argument(self):
        f = self.implementation()
        self.assertEqual(f(), 0)

    def test_starts_at_start_argument_value_if_passed(self):
        f = self.implementation(76)
        self.assertEqual(f(), 76)

    def test_calls_count_up_from_zero_without_start(self):
        expected_list = list(range(1000))
        f = self.implementation()
        results = [f() for _ in range(1000)]
        self.assertListEqual(results, expected_list)

    @parameterized.expand([
        ('start_0', 0, range(0, 1000)),
        ('start_1', 1, range(1, 1001)),
        ('start_500', 500, range(500, 1500)),
        ('start_neg_342', -342, range(-342, 658)),
    ])
    def test_calls_count_up_from_start(self, _name, start, expected):
        expected_list = list(expected)
        f = self.implementation(start)
        results = [f() for _ in range(1000)]
        self.assertListEqual(results, expected_list)

    def test_calls_to_separate_counters_count_independently(self):
        f = self.implementation()
        with self.subTest(func='f', call=1):
            self.assertEqual(f(), 0)
        with self.subTest(func='f', call=2):
            self.assertEqual(f(), 1)

        g = self.implementation()
        with self.subTest(func='f', call=3):
            self.assertEqual(f(), 2)
        with self.subTest(func='g', call=1):
            self.assertEqual(g(), 0)
        with self.subTest(func='f', call=4):
            self.assertEqual(f(), 3)
        with self.subTest(func='g', call=2):
            self.assertEqual(g(), 1)
        with self.subTest(func='g', call=3):
            self.assertEqual(g(), 2)

        h = self.implementation(10)
        with self.subTest(func='h', call=1):
            self.assertEqual(h(), 10)
        with self.subTest(func='f', call=5):
            self.assertEqual(f(), 4)
        with self.subTest(func='g', call=4):
            self.assertEqual(g(), 3)
        with self.subTest(func='h', call=2):
            self.assertEqual(h(), 11)
        with self.subTest(func='g', call=5):
            self.assertEqual(g(), 4)
        with self.subTest(func='h', call=3):
            self.assertEqual(h(), 12)
        with self.subTest(func='h', call=4):
            self.assertEqual(h(), 13)
        with self.subTest(func='g', call=6):
            self.assertEqual(g(), 5)
        with self.subTest(func='g', call=7):
            self.assertEqual(g(), 6)
        with self.subTest(func='f', call=6):
            self.assertEqual(f(), 5)
        with self.subTest(func='h', call=5):
            self.assertEqual(h(), 14)


@parameterized_class(('implementation_name',), [
    ('make_next_fibonacci',),
    ('make_next_fibonacci_alt',),
])
class TestMakeNextFibonacci(_NamedImplementationTestCase):
    """
    Tests for the make_next_fibonacci and make_next_fibonacci_alt functions.
    """

    def test_successive_fibonacci_numbers_are_returned(self):
        expected = _fib5k()
        f = self.implementation()
        actual = [f() for _ in range(5000)]
        self.assertListEqual(actual, expected)

    def test_calls_to_separate_functions_compute_independently(self):
        f = self.implementation()
        with self.subTest(func='f', call=1):
            self.assertEqual(f(), 0)
        with self.subTest(func='f', call=2):
            self.assertEqual(f(), 1)
        with self.subTest(func='f', call=3):
            self.assertEqual(f(), 1)
        with self.subTest(func='f', call=4):
            self.assertEqual(f(), 2)
        with self.subTest(func='f', call=5):
            self.assertEqual(f(), 3)

        g = self.implementation()
        with self.subTest(func='g', call=1):
            self.assertEqual(g(), 0)
        with self.subTest(func='f', call=6):
            self.assertEqual(f(), 5)
        with self.subTest(func='g', call=2):
            self.assertEqual(g(), 1)
        with self.subTest(func='f', call=7):
            self.assertEqual(f(), 8)
        with self.subTest(func='g', call=3):
            self.assertEqual(g(), 1)
        with self.subTest(func='f', call=8):
            self.assertEqual(f(), 13)
        with self.subTest(func='g', call=4):
            self.assertEqual(g(), 2)
        with self.subTest(func='f', call=9):
            self.assertEqual(f(), 21)
        with self.subTest(func='g', call=5):
            self.assertEqual(g(), 3)
        with self.subTest(func='f', call=10):
            self.assertEqual(f(), 34)

        with self.subTest(func='f', call=11):
            self.assertEqual(f(), 55)
        with self.subTest(func='f', call=12):
            self.assertEqual(f(), 89)
        with self.subTest(func='g', call=6):
            self.assertEqual(g(), 5)


@parameterized_class('implementation_name', [
    ('as_func',),
    ('as_closeable_func',),
])
class TestAsFunc(_NamedImplementationTestCase):
    """Tests for the as_func and as_closeable_func functions."""

    @parameterized.expand([
        ('range', lambda: range(3)),
        ('range_iterator', lambda: iter(range(3))),
        ('list', lambda: [0, 1, 2]),
        ('list_iterator', lambda: iter([0, 1, 2])),
        ('generator', lambda: (x for x in (0, 1, 2))),
    ])
    def test_returned_function_calls_next_on_iterable(self, _name, factory):
        f = self.implementation(factory())

        with self.subTest(call=1):
            self.assertEqual(f(), 0)
        with self.subTest(call=2):
            self.assertEqual(f(), 1)
        with self.subTest(call=3):
            self.assertEqual(f(), 2)

        with self.subTest(call=4):
            with self.assertRaises(StopIteration):
                f()

    def test_calls_to_separate_functions_iterate_independently(self):
        f = self.implementation([10, 20, 30])
        with self.subTest(func='f', call=1):
            self.assertEqual(f(), 10)
        with self.subTest(func='f', call=2):
            self.assertEqual(f(), 20)

        g = self.implementation(x**2 for x in itertools.count(2))
        with self.subTest(func='f', call=3):
            self.assertEqual(f(), 30)
        with self.subTest(func='g', call=1):
            self.assertEqual(g(), 4)
        with self.subTest(func='f', call=4):
            with self.assertRaises(StopIteration):
                f()

        with self.subTest(func='g', call=2):
            self.assertEqual(g(), 9)
        with self.subTest(func='g', call=3):
            self.assertEqual(g(), 16)


class TestAsCloseableFunc(unittest.TestCase):
    """
    Tests specific to the as_closeable_func function.

    These tests can be compared to those in TestAsCloseableFuncLimited (below).
    """

    @parameterized.expand([
        ('generator iterator', (i for i in itertools.count(1))),
        ('non-generator iterator', _CloseableNonGeneratorIterator(1)),
        ('generator iterable', _IterableWithGeneratorIterator(1)),
        ('non-generator iterable',
            _IterableWithCloseableNonGeneratorIterator(1)),
    ])
    def test_has_close_attribute_if_iterator_has_close(self, _name,
                                                       closeable_iterator):
        f = functions.as_closeable_func(closeable_iterator)
        self.assertTrue(hasattr(f, 'close'))

    @parameterized.expand([
        ('generator iterator', (i for i in itertools.count(1))),
        ('non-generator iterator', _CloseableNonGeneratorIterator(1)),
        ('generator iterable', _IterableWithGeneratorIterator(1)),
        ('non-generator iterable',
            _IterableWithCloseableNonGeneratorIterator(1)),
    ])
    def test_can_close_if_iterator_has_close(self, _name, it):
        f = functions.as_closeable_func(it)

        with contextlib.closing(f):
            with self.subTest('before closing', call=1):
                self.assertEqual(f(), 1)
            with self.subTest('before closing', call=2):
                self.assertEqual(f(), 2)

        with self.subTest('after closing', call=3):
            with self.assertRaises(StopIteration):
                f()

    @parameterized.expand([
        ('itertools.count', itertools.count(1)),
        ('list iterator', iter([1, 2, 3])),
        ('list', [1, 2, 3]),
        ('closeable iterable', _CloseableIterableWithNonCloseableIterator(1)),
    ])
    def test_no_close_attribute_if_iterator_has_no_close(self, _name, it):
        f = functions.as_closeable_func(it)
        self.assertFalse(hasattr(f, 'close'))

    @parameterized.expand([
        ('itertools.count', itertools.count(1)),
        ('list iterator', iter([1, 2, 3])),
        ('list', [1, 2, 3]),
        ('closeable iterable', _CloseableIterableWithNonCloseableIterator(1)),
    ])
    def test_cannot_close_if_iterator_has_no_close(self, _name, it):
        f = functions.as_closeable_func(it)

        with self.assertRaises(AttributeError):
            with contextlib.closing(f):
                with self.subTest('before attempting close', call=1):
                    self.assertEqual(f(), 1)
                with self.subTest('before attempting close', call=2):
                    self.assertEqual(f(), 2)

        with self.subTest('after attempting close', call=3):
            self.assertEqual(f(), 3)


@parameterized_class(('implementation_name',), [
    ('as_func_limited',),
    ('as_func_limited_alt',),
    ('as_closeable_func_limited',),
])
class TestAsFuncLimited(_NamedImplementationTestCase):
    """Tests for as_func_limited and related functions."""

    @parameterized.expand([
        ('range', lambda: range(3)),
        ('range_iterator', lambda: iter(range(3))),
        ('list', lambda: [0, 1, 2]),
        ('list_iterator', lambda: iter([0, 1, 2])),
        ('generator', lambda: (x for x in (0, 1, 2))),
    ])
    def test_returned_function_gives_next_item_or_sentinel(self, _name,
                                                           factory):
        f = self.implementation(factory(), 42)

        with self.subTest(call=1):
            self.assertEqual(f(), 0)
        with self.subTest(call=2):
            self.assertEqual(f(), 1)
        with self.subTest(call=3):
            self.assertEqual(f(), 2)

        with self.subTest(call=4):
            self.assertEqual(f(), 42)
        with self.subTest(call=5):
            self.assertEqual(f(), 42)
        with self.subTest(call=6):
            self.assertEqual(f(), 42)

    def test_calls_to_separate_functions_iterate_independently(self):
        f = self.implementation([10, 20, 30], -1)
        with self.subTest(func='f', call=1):
            self.assertEqual(f(), 10)
        with self.subTest(func='f', call=2):
            self.assertEqual(f(), 20)

        g = self.implementation((x**2 for x in itertools.count(2)), -2)
        with self.subTest(func='f', call=3):
            self.assertEqual(f(), 30)
        with self.subTest(func='g', call=1):
            self.assertEqual(g(), 4)
        with self.subTest(func='f', call=4):
            self.assertEqual(f(), -1)

        with self.subTest(func='g', call=2):
            self.assertEqual(g(), 9)
        with self.subTest(func='g', call=3):
            self.assertEqual(g(), 16)
        with self.subTest(func='f', call=5):
            self.assertEqual(f(), -1)

        h = self.implementation((), -3)
        with self.subTest(func='g', call=4):
            self.assertEqual(g(), 25)
        with self.subTest(func='h', call=1):
            self.assertEqual(h(), -3)
        with self.subTest(func='f', call=6):
            self.assertEqual(f(), -1)


class TestAsCloseableFuncLimited(unittest.TestCase):
    """
    Tests specific to the as_closeable_func_limited function.

    These tests can be compared to those in TestAsCloseableFunc (above).
    """

    @parameterized.expand([
        ('generator iterator', (i for i in itertools.count(1))),
        ('non-generator iterator', _CloseableNonGeneratorIterator(1)),
        ('generator iterable', _IterableWithGeneratorIterator(1)),
        ('non-generator iterable',
            _IterableWithCloseableNonGeneratorIterator(1)),
    ])
    def test_has_close_attribute_if_iterator_has_close(self, _name,
                                                       closeable_iterator):
        f = functions.as_closeable_func_limited(closeable_iterator, -17)
        self.assertTrue(hasattr(f, 'close'))

    @parameterized.expand([
        ('generator iterator', (i for i in itertools.count(1))),
        ('non-generator iterator', _CloseableNonGeneratorIterator(1)),
        ('generator iterable', _IterableWithGeneratorIterator(1)),
        ('non-generator iterable',
            _IterableWithCloseableNonGeneratorIterator(1)),
    ])
    def test_can_close_if_iterator_has_close(self, _name, it):
        f = functions.as_closeable_func_limited(it, -17)

        with contextlib.closing(f):
            with self.subTest('before closing', call=1):
                self.assertEqual(f(), 1)
            with self.subTest('before closing', call=2):
                self.assertEqual(f(), 2)

        with self.subTest('after closing', call=3):
            self.assertEqual(f(), -17)
        with self.subTest('after closing', call=4):
            self.assertEqual(f(), -17)

    @parameterized.expand([
        ('itertools.count', itertools.count(1)),
        ('list iterator', iter([1, 2, 3])),
        ('list', [1, 2, 3]),
        ('closeable iterable', _CloseableIterableWithNonCloseableIterator(1)),
    ])
    def test_no_close_attribute_if_iterator_has_no_close(self, _name, it):
        f = functions.as_closeable_func_limited(it, -17)
        self.assertFalse(hasattr(f, 'close'))

    @parameterized.expand([
        ('itertools.count', itertools.count(1)),
        ('list iterator', iter([1, 2, 3])),
        ('list', [1, 2, 3]),
        ('closeable iterable', _CloseableIterableWithNonCloseableIterator(1)),
    ])
    def test_cannot_close_if_iterator_has_no_close(self, _name, it):
        f = functions.as_closeable_func_limited(it, -17)

        with self.assertRaises(AttributeError):
            with contextlib.closing(f):
                with self.subTest('before attempting close', call=1):
                    self.assertEqual(f(), 1)
                with self.subTest('before attempting close', call=2):
                    self.assertEqual(f(), 2)

        with self.subTest('after attempting close', call=3):
            self.assertEqual(f(), 3)


@parameterized_class(('implementation_name',), [
    ('as_iterator_limited',),
    ('as_iterator_limited_alt',),
    ('CallableIterator',),
    ('as_closeable_iterator_limited',)
])
class TestAsIteratorLimited(_NamedImplementationTestCase):
    """Tests for as_iterator_limited and related functions/classes."""

    def test_iterator_is_fixed_point_of_iter(self):
        """Calling iter on the iterator gives the same iterator object back."""
        it = self.implementation(lambda: 'foo', 'bar')
        self.assertIs(iter(it), it)

    def test_iterator_calls_simple_f_until_sentinel(self):
        d = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e'}
        k = 'a'

        def f():
            nonlocal k
            k = d[k]
            return k

        it = self.implementation(f, 'd')
        with self.subTest(call=1):
            self.assertEqual(next(it), 'b')
        with self.subTest(call=2):
            self.assertEqual(next(it), 'c')
        with self.subTest(call=3):
            with self.assertRaises(StopIteration):
                next(it)

    @parameterized.expand([
        ('make_counter', 2000, list(range(2000))),
        ('make_counter_alt', 2000, list(range(2000))),
        ('make_next_fibonacci', 89, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
        ('make_next_fibonacci_alt', 89, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
    ])
    def test_iterator_calls_f_until_sentinel(self, f_name, sentinel, expected):
        """
        Iterators on synthesized iterator-like functions "round trip."

        Calling as_iterator_limited{,_alt} on synthesized functions that
        themselves behave like calling next() on an iterator behaves as
        expected.
        """
        f_impl = getattr(functions, f_name)
        it = self.implementation(f_impl(), sentinel)
        with self.subTest('is an iterator'):
            self.assertIsInstance(it, Iterator)
        with self.subTest('has correct values'):
            self.assertListEqual(list(it), expected)

    def test_next_on_exhausted_iterator_raises_without_calling(self):
        """After next() raises StopIteration, it always does so again."""
        calls = 0

        def f():
            nonlocal calls
            calls += 1
            return 42

        it = self.implementation(f, 42)

        with self.subTest("1 next() call - f called once"):
            with self.assertRaises(StopIteration):
                next(it)
            self.assertEqual(calls, 1)

        with self.subTest("2 next() calls - f should not be called again"):
            with self.assertRaises(StopIteration):
                next(it)
            self.assertEqual(calls, 1)

        with self.subTest("3 next() calls - f should not be called again"):
            with self.assertRaises(StopIteration):
                next(it)
            self.assertEqual(calls, 1)


class TestAsCloseableIteratorLimited(unittest.TestCase):
    """Tests specific to the as_closeable_iterator_limited function."""

    def test_result_is_generator(self):
        """The result must be a generator, not just any iterator."""
        it = functions.as_closeable_iterator_limited(lambda: 42, 42)
        self.assertTrue(inspect.isgenerator(it))

    def test_function_without_close_ok_when_not_started_not_closed(self):
        """f need not be closeable. (Test with no calls to next, 1 of 2.)"""
        a = [10, 20, 30, 40]
        it = functions.as_closeable_iterator_limited(a.pop, 20)
        r = weakref.ref(it)
        try:
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_not_started_but_closed(self):
        """f need not be closeable. (Test with no calls to next, 2 of 2.)"""
        a = [10, 20, 30, 40, 50]
        it = functions.as_closeable_iterator_limited(a.pop, 20)
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_started_not_closed(self):
        """f need not be closeable. (Test with one call to next, 1 of 2.)"""
        a = [10, 20, 30, 40]
        it = functions.as_closeable_iterator_limited(a.pop, 20)
        next(it)
        r = weakref.ref(it)
        try:
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_started_then_closed(self):
        """f need not be closeable. (Test with one call to next, 2 of 2.)"""
        a = [10, 20, 30, 40, 50]
        it = functions.as_closeable_iterator_limited(a.pop, 20)
        next(it)
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_finished(self):
        """f need not be closeable. (Test exhausting the generator, 1 of 2.)"""
        a = [10, 20, 30, 40]
        it = functions.as_closeable_iterator_limited(a.pop, 20)
        try:
            collections.deque(it, maxlen=0)  # Exhaust the generator.
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_even_if_finished_then_closed(self):
        """f need not be closeable. (Test exhausting the generator, 2 of 2.)"""
        a = [10, 20, 30, 40]
        it = functions.as_closeable_iterator_limited(a.pop, 20)
        collections.deque(it, maxlen=0)  # Exhaust the generator.
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_on_exception(self):
        """
        f need not be closeable. (Test raising exceptions, 1 of 2.)

        In the example here, ZeroDivisionError must be raised. Other
        exceptions, such as AttributeError, must not be raised.
        """
        a = [-3, -2, -1, 0, 1, 2]
        it = functions.as_closeable_iterator_limited(lambda: 1 / a.pop(), -2)
        with self.assertRaises(ZeroDivisionError):
            collections.deque(it, maxlen=0)

    def test_function_without_close_ok_on_exception_then_closed(self):
        """f need not be closeable. (Test raising exceptions, 2 of 2.)"""
        a = [-3, -2, -1, 0, 1, 2]
        it = functions.as_closeable_iterator_limited(lambda: 1 / a.pop(), -2)
        with contextlib.suppress(ZeroDivisionError):
            collections.deque(it, maxlen=0)
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_closeable_function_closed_after_not_started_not_closed(self):
        """close called if present. (Test with no calls to next, 1 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, 20)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()

        with self.subTest('close called on finalization'):
            r = weakref.ref(it)
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
            mock_close.assert_called_once()

    def test_closeable_function_closed_after_not_started_but_closed(self):
        """close called if present. (Test with no calls to next, 2 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, 20)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()
        with self.subTest('closing generator closes function'):
            it.close()
            mock_close.assert_called_once()

    def test_closeable_function_closed_after_started_not_closed(self):
        """close called if present. (Test with one call to next, 1 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, 20)
        next(it)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()

        with self.subTest('close called on finalization'):
            r = weakref.ref(it)
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
            mock_close.assert_called_once()

    def test_closeable_function_closed_after_started_then_closed(self):
        """close called if present. (Test with one call to next, 2 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, 20)
        next(it)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()
        with self.subTest('closing generator closes function'):
            it.close()
            mock_close.assert_called_once()

    def test_closeable_function_closed_when_finished(self):
        """close called if present. (Test exhausting the generator.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, 20)
        with self.subTest('close not called way too early'):
            mock_close.assert_not_called()
        with self.subTest('exhausting generator closes function'):
            collections.deque(it, maxlen=0)  # Exhaust the generator.
            mock_close.assert_called_once()

    def test_closeable_function_closed_on_exception_in_first_call(self):
        """close called if present. (Test raising exceptions, 1 of 2.)"""
        a = [-3, -2, -1, 0]

        def f():
            return 1 / a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, -2)

        with self.subTest('close not called way too early'):
            mock_close.assert_not_called()

        with self.subTest('failed call to next propagates correct exception'):
            with self.assertRaises(ZeroDivisionError):
                next(it)

        with self.subTest('failed call to next closed the function'):
            mock_close.assert_called_once()

    def test_closeable_function_closed_on_exception(self):
        """close called if present. (Test raising exceptions, 2 of 2.)"""
        a = [-3, -2, -1, 0, 1]

        def f():
            return 1 / a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator_limited(f, -2)
        next(it)

        with self.subTest('close not called too early'):
            mock_close.assert_not_called()

        with self.subTest('failed call to next propagates correct exception'):
            with self.assertRaises(ZeroDivisionError):
                next(it)

        with self.subTest('failed call to next closed the function'):
            mock_close.assert_called_once()


@parameterized_class(('implementation_name',), [
    ('as_iterator',),
    ('as_iterator_alt',),
    ('as_closeable_iterator',),
])
class TestAsIterator(_NamedImplementationTestCase):
    """Tests for the as_iterator and as_iterator_alt functions."""

    def test_iterator_calls_simple_f(self):
        d = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e', 'e': 'a'}
        k = 'a'

        def f():
            nonlocal k
            k = d[k]
            return k

        it = self.implementation(f)

        with self.subTest('is an iterator'):
            self.assertIsInstance(it, Iterator)

        with self.subTest('has correct values'):
            prefix = list(itertools.islice(it, 12))
            self.assertListEqual(prefix, list('bcdeabcdeabc'))

    @parameterized.expand([
        ('make_counter', 2000, list(range(2000))),
        ('make_counter_alt', 2000, list(range(2000))),
        ('make_next_fibonacci', 11, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
        ('make_next_fibonacci_alt', 11, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
    ])
    def test_iterator_calls_f(self, f_name, prefix_length, expected):
        f_impl = getattr(functions, f_name)

        it = self.implementation(f_impl())

        with self.subTest('is an iterator'):
            self.assertIsInstance(it, Iterator)

        with self.subTest('has correct values'):
            prefix = list(itertools.islice(it, prefix_length))
            self.assertListEqual(prefix, expected)


class TestAsCloseableIterator(unittest.TestCase):
    """
    Tests specific to the as_closeable_iterator function.

    Compare to TestAsCloseableIteratorLimited (above). The tests are similar,
    but besides testing a different function and calling it differently (with
    one argument instead of two), this doesn't have tests for "finished"
    states, since here there is no sentinel value the function can return to
    indicate that it is finished.
    """

    def test_result_is_generator(self):
        """The result must be a generator, not just any iterator."""
        it = functions.as_closeable_iterator(lambda: 42)
        self.assertTrue(inspect.isgenerator(it))

    def test_function_without_close_ok_when_not_started_not_closed(self):
        """f need not be closeable. (Test with no calls to next, 1 of 2.)"""
        a = [10, 20, 30, 40]
        it = functions.as_closeable_iterator(a.pop)
        r = weakref.ref(it)
        try:
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_not_started_but_closed(self):
        """f need not be closeable. (Test with no calls to next, 2 of 2.)"""
        a = [10, 20, 30, 40, 50]
        it = functions.as_closeable_iterator(a.pop)
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_started_not_closed(self):
        """f need not be closeable. (Test with one call to next, 1 of 2.)"""
        a = [10, 20, 30, 40]
        it = functions.as_closeable_iterator(a.pop)
        next(it)
        r = weakref.ref(it)
        try:
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_when_started_then_closed(self):
        """f need not be closeable. (Test with one call to next, 2 of 2.)"""
        a = [10, 20, 30, 40, 50]
        it = functions.as_closeable_iterator(a.pop)
        next(it)
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_function_without_close_ok_on_exception(self):
        """
        f need not be closeable. (Test raising exceptions, 1 of 2.)

        In the example here, ZeroDivisionError must be raised. Other
        exceptions, such as AttributeError, must not be raised.
        """
        a = [-3, -2, -1, 0, 1, 2]
        it = functions.as_closeable_iterator(lambda: 1 / a.pop())
        with self.assertRaises(ZeroDivisionError):
            collections.deque(it, maxlen=0)

    def test_function_without_close_ok_on_exception_then_closed(self):
        """f need not be closeable. (Test raising exceptions, 2 of 2.)"""
        a = [-3, -2, -1, 0, 1, 2]
        it = functions.as_closeable_iterator(lambda: 1 / a.pop())
        with contextlib.suppress(ZeroDivisionError):
            collections.deque(it, maxlen=0)
        try:
            it.close()
        except AttributeError as error:
            self.fail(f'Got AttributeError: {error}')

    def test_closeable_function_closed_after_not_started_not_closed(self):
        """close called if present. (Test with no calls to next, 1 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator(f)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()

        with self.subTest('close called on finalization'):
            r = weakref.ref(it)
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
            mock_close.assert_called_once()

    def test_closeable_function_closed_after_not_started_but_closed(self):
        """close called if present. (Test with no calls to next, 2 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator(f)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()
        with self.subTest('closing generator closes function'):
            it.close()
            mock_close.assert_called_once()

    def test_closeable_function_closed_after_started_not_closed(self):
        """close called if present. (Test with one call to next, 1 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator(f)
        next(it)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()

        with self.subTest('close called on finalization'):
            r = weakref.ref(it)
            del it
            testing.collect_if_not_ref_counting()
            if r() is not None:
                raise Exception(
                    "unreferenced result exists, can't test implicit close")
            mock_close.assert_called_once()

    def test_closeable_function_closed_after_started_then_closed(self):
        """close called if present. (Test with one call to next, 2 of 2.)"""
        a = [10, 20, 30, 40]

        def f():
            return a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator(f)
        next(it)
        with self.subTest('close not called too early'):
            mock_close.assert_not_called()
        with self.subTest('closing generator closes function'):
            it.close()
            mock_close.assert_called_once()

    def test_closeable_function_closed_on_exception_in_first_call(self):
        """close called if present. (Test raising exceptions, 1 of 2.)"""
        a = [-3, -2, -1, 0]

        def f():
            return 1 / a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator(f)

        with self.subTest('close not called way too early'):
            mock_close.assert_not_called()

        with self.subTest('failed call to next propagates correct exception'):
            with self.assertRaises(ZeroDivisionError):
                next(it)

        with self.subTest('failed call to next closed the function'):
            mock_close.assert_called_once()

    def test_closeable_function_closed_on_exception(self):
        """close called if present. (Test raising exceptions, 2 of 2.)"""
        a = [-3, -2, -1, 0, 1]

        def f():
            return 1 / a.pop()

        mock_close = unittest.mock.Mock()
        f.close = mock_close
        it = functions.as_closeable_iterator(f)
        next(it)

        with self.subTest('close not called too early'):
            mock_close.assert_not_called()

        with self.subTest('failed call to next propagates correct exception'):
            with self.assertRaises(ZeroDivisionError):
                next(it)

        with self.subTest('failed call to next closed the function'):
            mock_close.assert_called_once()


@parameterized_class(('implementation_name',), [
    ('count_tree_nodes',),
    ('count_tree_nodes_alt',),
])
class TestCountTreeNodes(_NamedImplementationTestCase):
    """Tests for the count_tree_nodes and count_tree_nodes_alt functions."""

    def test_str_has_one_node(self):
        """Strings (like other non-tuple iterables) are taken as leaves."""
        root = 'a parrot'
        result = self.implementation(root)
        self.assertEqual(result, 1)

    def test_empty_tuple_has_one_node(self):
        """An empty tuple is taken as a leaf."""
        root = ()
        result = self.implementation(root)
        self.assertEqual(result, 1)

    def test_small_nontrivial_nested_tuple_of_ints_is_fully_traversed(self):
        """A nested tuple of varying depth has its internal and leaf nodes."""
        root = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
        result = self.implementation(root)
        self.assertEqual(result, 22)

    def test_list_containing_nontrivial_nested_tuple_has_only_one_node(self):
        """A list, even of tuple(s), is taken as a leaf (so not traversed)."""
        root = [((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))]
        result = self.implementation(root)
        self.assertEqual(result, 1)

    @parameterized.expand([
        ('n_equals_0', 0, 1),
        ('n_equals_1', 1, 1),
        ('n_equals_2', 2, 3),
        ('n_equals_3', 3, 5),
        ('n_equals_4', 4, 9),
        ('n_equals_5', 5, 15),
        ('n_equals_6', 6, 25),
        ('n_equals_7', 7, 41),
        ('n_equals_8', 8, 67),
        ('n_equals_9', 9, 109),
        ('n_equals_10', 10, 177),
        ('n_equals_11', 11, 287),
        ('n_equals_12', 12, 465),
        ('n_equals_13', 13, 753),
        ('n_equals_14', 14, 1219),
        ('n_equals_15', 15, 1973),
        ('n_equals_16', 16, 3193),
    ])
    def test_fibonacci_structure_is_fully_traversed(self, _name, n, expected):
        """Structures of Fibonacci subproblems have internal and leaf nodes."""
        root = fibonacci.fib_nest(n)
        result = self.implementation(root)
        self.assertEqual(result, expected)


class _StdoutCapturingTestCase(unittest.TestCase):
    """Test fixture mixin that redirects standard output."""

    def setUp(self):
        """Redirect standard output."""
        super().setUp()
        self._old_stdout = sys.stdout
        self._stdout = sys.stdout = io.StringIO()

    def tearDown(self):
        """Undo the redirection of standard output."""
        sys.stdout = self._old_stdout
        super().tearDown()

    @property
    def out(self):
        """The text sent so far to stdout during a single test."""
        return self._stdout.getvalue()


class TestCountTreeNodesInstrumented(_StdoutCapturingTestCase):
    """Tests for the count_tree_nodes_instrumented function."""

    def setUp(self):
        """Arrange a test by checking a precondition and redirecting stdout."""
        if functions.count_tree_nodes is not _original_count_tree_nodes:
            # Force an error (rather than mere failure).
            raise Exception('count_tree_nodes ALREADY wrong at START of test')

        super().setUp()  # Capture stdout for the duration of the test.

    def test_function_patched_and_restored_when_no_exception_is_raised(self):
        """count_tree_nodes is patched/unpatched in the absence of errors."""
        root1 = recursion.make_deep_tuple(2)
        result1 = functions.count_tree_nodes_instrumented(root1)
        output1 = self.out

        with self.subTest(run=1, instrumented=True, check='return value'):
            self.assertEqual(result1, 3)

        with self.subTest(run=1, instrumented=True, check='printed output'):
            self.assertEqual(output1, 'count_tree_nodes(()) -> 1\n'
                                      'count_tree_nodes(((),)) -> 2\n'
                                      'count_tree_nodes((((),),)) -> 3\n')

        with self.subTest(run=1, instrumented=True,
                          check='restores original function'):
            self.assertIs(functions.count_tree_nodes,
                          _original_count_tree_nodes,
                          'failed to restore count_tree_nodes')

        # Call count_tree_nodes to check that its normal behavior is restored.
        root2 = recursion.make_deep_tuple(3)
        result2 = functions.count_tree_nodes(root2)

        with self.subTest(run=2, instrumented=False, check='return value'):
            self.assertEqual(result2, 4)

        with self.subTest(run=2, instrumented=False, check='printed output'):
            self.assertEqual(self.out, output1, 'no more should be printed')

    def test_function_patched_and_restored_when_an_exception_propagates(self):
        """
        count_tree_nodes is patched/unpatched even in the presence of errors.
        """
        root1 = recursion.make_deep_tuple(5000)
        with self.assertRaises(RecursionError):
            functions.count_tree_nodes_instrumented(root1)

        with self.subTest(run=1, instrumented=True, check='printed output'):
            self.assertEqual(self.out, '', 'no output should be printed')

        with self.subTest(run=1, instrumented=True,
                          check='restores original function'):
            self.assertIs(functions.count_tree_nodes,
                          _original_count_tree_nodes,
                          'failed to restore count_tree_nodes')

        # Call count_tree_nodes to check that its normal behavior is restored.
        root2 = ((2, 7, 1), (8, 6), (9, (4, 5)), ((((5, 4), 3), 2), 1))
        result2 = functions.count_tree_nodes(root2)

        with self.subTest(run=2, instrumented=False, check='return value'):
            self.assertEqual(result2, 22)

        with self.subTest(run=2, instrumented=False, check='printed output'):
            self.assertEqual(self.out, '', 'no output should be printed')

    # TODO: Maybe add a test corresponding to the doctest using fib_nest(3).


class TestReportAttributes(_StdoutCapturingTestCase):
    """Tests for the report_attributes function."""

    def test_message_prints_if_no_non_metadata_attributes(self):
        functions.report_attributes(lambda x: x**2)
        self.assertEqual(self.out, 'No non-metadata attributes.\n')

    def test_builtin_has_no_non_metadata_attributes(self):
        functions.report_attributes(len)
        self.assertEqual(self.out, 'No non-metadata attributes.\n')

    def test_one_non_metadata_attribute_prints_like_assignment(self):
        def greet(value):
            print(greet.fmt.format(value))

        greet.fmt = 'Hello, {}!'

        functions.report_attributes(greet)
        self.assertEqual(self.out, "greet.fmt = 'Hello, {}!'\n")

    def test_two_non_metadata_attributes_print_like_assignments(self):
        expected = "square.foo = 42\nsquare.bar = 'seventy-six'\n"

        def square(x):
            return x**2

        square.foo = 42
        square.bar = 'seventy-six'

        functions.report_attributes(square)
        self.assertEqual(self.out, expected)


class TestFuncFilter(unittest.TestCase):
    """Tests for the func_filter function."""

    def test_none_satisfying_is_empty(self):
        """When no items satisfy the predicate, the result is empty."""
        get_number = unittest.mock.Mock()
        get_number.side_effect = itertools.count()

        result_func = functions.func_filter(lambda n: n < 0, get_number, 3)

        with self.subTest('initial result is sentinel'):
            self.assertEqual(result_func(), 3)
        with self.subTest('subsequent call gives sentinel'):
            self.assertEqual(result_func(), 3)
        with self.subTest('4 input calls: 0, 1, 2, <sentinel>'):
            self.assertEqual(get_number.call_count, 4)

    def test_some_satisfying_gives_those(self):
        """When only some satisfy the predicate, those are the result."""
        get_word = unittest.mock.Mock()
        get_word.side_effect = ['ham', 'spam', 'foo', 'eggs', 'done', 'a', 'b']

        result_func = functions.func_filter(lambda x: len(x) == 3,
                                            get_word, 'done')

        with self.subTest('first result is first matching word'):
            self.assertEqual(result_func(), 'ham')
        with self.subTest('second result is second matching word'):
            self.assertEqual(result_func(), 'foo')
        with self.subTest('third call gives sentinel'):
            self.assertEqual(result_func(), 'done')
        with self.subTest('subsequent call gives sentinel'):
            self.assertEqual(result_func(), 'done')
        with self.subTest('5 input calls: ham, spam, foo, eggs, <sentinel>'):
            self.assertEqual(get_word.call_count, 5)

    def test_none_predicate_filters_truthy(self):
        """A predicate of None checks the items themselves."""
        sentinel = object()
        mixed = ('p', 'xy', [3], (1, 2, 3), 'c')
        suffixes = (seq[1:] for seq in mixed)
        get_suffix = unittest.mock.Mock()
        get_suffix.side_effect = itertools.chain(suffixes, (sentinel,))

        result_func = functions.func_filter(None, get_suffix, sentinel)

        with self.subTest('first result is first truthy (nonempty) suffix'):
            self.assertEqual(result_func(), 'y')
        with self.subTest('second result is second truthy (nonempty) suffix'):
            self.assertEqual(result_func(), (2, 3))
        with self.subTest('third call gives sentinel'):
            self.assertIs(result_func(), sentinel)
        with self.subTest('subsequent call gives sentinel'):
            self.assertIs(result_func(), sentinel)
        with self.subTest('6 input calls: the 5 suffixes, then the sentinel'):
            self.assertEqual(get_suffix.call_count, 6)

    def test_none_predicate_filters_truthy_even_if_none(self):
        """A predicate of None gets nothing through if all are falsy."""
        sentinel = object()
        get_empty = unittest.mock.Mock()
        get_empty.side_effect = ([], (), {}, set(), sentinel, '')

        result_func = functions.func_filter(None, get_empty, sentinel)

        with self.subTest('initial result is sentinel'):
            self.assertIs(result_func(), sentinel)
        with self.subTest('subsequent call gives sentinel'):
            self.assertIs(result_func(), sentinel)
        with self.subTest('5 input calls: [], (), {}, set(), <sentinel>'):
            self.assertEqual(get_empty.call_count, 5)

    def test_none_predicate_filters_truthy_even_if_all(self):
        """A predicate of None lets everything through if none are falsy."""
        get_word = unittest.mock.Mock()
        get_word.side_effect = ['hello', 'glorious', 'world', '!', '??', '...']

        result_func = functions.func_filter(None, get_word, '!')

        with self.subTest('first result is first word'):
            self.assertEqual(result_func(), 'hello')
        with self.subTest('second result is second word'):
            self.assertEqual(result_func(), 'glorious')
        with self.subTest('third result is third word'):
            self.assertEqual(result_func(), 'world')
        with self.subTest('fourth call gives sentinel'):
            self.assertEqual(result_func(), '!')
        with self.subTest('subsequent call gives sentinel'):
            self.assertEqual(result_func(), '!')
        with self.subTest('4 input calls: hello, glorious, world, <sentinel>'):
            self.assertEqual(get_word.call_count, 4)

    def test_infinite_source_filters_lazily(self):
        """We can get a prefix, filtering a some-truthy infinite input."""
        get_number = unittest.mock.Mock()
        get_number.side_effect = itertools.count()

        result_func = functions.func_filter(lambda k: k % 2,
                                            get_number, object())

        with self.subTest('correct return values when called'):
            expected = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
            actual = [result_func() for _ in range(13)]
            self.assertEqual(actual, expected)

        # If the above subtest failed, such as with an exception, then this
        # result will almost certainly be wrong... but in that situation, we
        # almost certainly do want to inspect this result, too.
        with self.subTest('26 input calls: 0, 1, ..., 24, 25 (stop)'):
            self.assertEqual(get_number.call_count, 26)

    def test_call_can_skip_many_filtered_out_values(self):
        """
        A call to the result function may call the input function many times.
        """
        get_number = unittest.mock.Mock()
        get_number.side_effect = itertools.count()

        result_func = functions.func_filter(lambda k: k > 10_000,
                                            get_number, object())

        with self.subTest('first result is first matching number'):
            self.assertEqual(result_func(), 10_001)
        with self.subTest('10,002 input calls: 0, ..., 10_000, 10_001 (stop)'):
            self.assertEqual(get_number.call_count, 10_002)

    def test_predicate_not_called_on_sentinel(self):
        """
        The predicate may only be valid on values returned before the sentinel.

        This checks that it is never called on the sentinel value itself.
        """
        sentinel = object()
        get_word = unittest.mock.Mock()
        get_word.side_effect = ['hello', 'glorious', 'world', sentinel]

        result_func = functions.func_filter(lambda w: len(w) == 5,
                                            get_word, sentinel)

        try:
            while result_func() != sentinel:
                pass
        except TypeError as error:
            if str(error) == "object of type 'object' has no len()":
                self.fail(f'predicate called on sentinel ({error})')
            raise

    def test_predicate_called_on_all_input_values(self):
        """
        The predicate is called on each input value before the sentinel.

        If test_predicate_not_called_on_sentinel fails, this should fail too,
        since this asserts the arguments and order of all predicate calls. That
        test case is intended to clearly reveal that bug if present (and to
        express that it is a bug), while this test case is intended to guard
        against other possible bugs that cannot all be predicted.
        """
        get_word = unittest.mock.Mock()
        get_word.side_effect = ['first', 'second', 'third', 'fourth', 'fifth']

        predicate_arguments = []

        def predicate(word):
            predicate_arguments.append(word)
            return len(word) == 5

        result_func = functions.func_filter(predicate, get_word, 'fourth')

        for _ in range(25):
            result_func()

        self.assertListEqual(predicate_arguments, ['first', 'second', 'third'])


if __name__ == '__main__':
    unittest.main()
