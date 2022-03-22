#!/usr/bin/env python

"""Tests for the functions in functions.py."""

from collections.abc import Iterator
import functools
import itertools
import unittest

from parameterized import parameterized, parameterized_class

import functions


# TODO: Replace this with a parameterized-decorator factory (so it will be a
# decorator factory factory) that takes a module name and returns a decorator
# factory that takes a variable number of implementation name arguments and
# behaves like @parameterized.parameterized_class as used in the tests below.
# Write tests for it, and also use it instead of @parameterized_class below.
#
# If you name it make_implementation_parameterizer, usage will look like:
#
#     for_implementations = make_implementation_parameterizer(functions)
#
#     @for_implementations('make_counter', 'make_counter_alt')
#     class TestMakeCounter(unittest.TestCase):
#         ...
#
#     @for_implementations('make_next_fibonacci', 'make_next_fibonacci_alt')
#     class TestMakeNextFibonacci(unittest.TestCase):
#         ...
#
# The parameterized decorator (like for_implementations in the above example)
# returned by the decorator factory factory should accept arbitrarily many
# positional arguments representing names of entities to test.
class _NamedImplementationTestCase(unittest.TestCase):
    """
    Base class to test entities in the functions module by their names.

    The recommended use is to inherit from this class and assign an unqualified
    attribute name (most often a function name) to the implementation_name
    class attribute by using the @parameterized.parameterized_class decorator.
    """

    __slots__ = ()

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

    __slots__ = ()

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
        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)

        g = self.implementation()
        self.assertEqual(f(), 2)
        self.assertEqual(g(), 0)
        self.assertEqual(f(), 3)
        self.assertEqual(g(), 1)
        self.assertEqual(g(), 2)

        h = self.implementation(10)
        self.assertEqual(h(), 10)
        self.assertEqual(f(), 4)
        self.assertEqual(g(), 3)
        self.assertEqual(h(), 11)
        self.assertEqual(g(), 4)
        self.assertEqual(h(), 12)
        self.assertEqual(h(), 13)
        self.assertEqual(g(), 5)
        self.assertEqual(g(), 6)
        self.assertEqual(f(), 5)
        self.assertEqual(h(), 14)


@parameterized_class(('implementation_name',), [
    ('make_next_fibonacci',),
    ('make_next_fibonacci_alt',),
])
class TestMakeNextFibonacci(_NamedImplementationTestCase):
    """
    Tests for the make_next_fibonacci and make_next_fibonacci_alt functions.
    """

    __slots__ = ()

    def test_successive_fibonacci_numbers_are_returned(self):
        expected = _fib5k()
        f = self.implementation()
        actual = [f() for _ in range(5000)]
        self.assertListEqual(actual, expected)

    def test_calls_to_separate_functions_compute_independently(self):
        f = self.implementation()
        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 2)
        self.assertEqual(f(), 3)

        g = self.implementation()
        self.assertEqual(g(), 0)
        self.assertEqual(f(), 5)
        self.assertEqual(g(), 1)
        self.assertEqual(f(), 8)
        self.assertEqual(g(), 1)
        self.assertEqual(f(), 13)
        self.assertEqual(g(), 2)
        self.assertEqual(f(), 21)
        self.assertEqual(g(), 3)
        self.assertEqual(f(), 34)

        self.assertEqual(f(), 55)
        self.assertEqual(f(), 89)
        self.assertEqual(g(), 5)


class TestAsFunc(unittest.TestCase):
    """Tests for the as_func function."""

    __slots__ = ()

    @parameterized.expand([
        ('range', range(3)),
        ('range_iterator', iter(range(3))),
        ('list', [0, 1, 2]),
        ('list_iterator', iter([0, 1, 2])),
        ('generator', (x for x in (0, 1, 2))),
    ])
    def test_returned_function_calls_next_on_iterable(self, _name, iterable):
        f = functions.as_func(iterable)

        self.assertEqual(f(), 0)
        self.assertEqual(f(), 1)
        self.assertEqual(f(), 2)

        with self.assertRaises(StopIteration):
            f()

    def test_calls_to_separate_functions_iterate_independently(self):
        f = functions.as_func([10, 20, 30])
        self.assertEqual(f(), 10)
        self.assertEqual(f(), 20)

        g = functions.as_func(x**2 for x in itertools.count(2))
        self.assertEqual(f(), 30)
        self.assertEqual(g(), 4)
        with self.assertRaises(StopIteration):
            f()

        self.assertEqual(g(), 9)
        self.assertEqual(g(), 16)


@parameterized_class(('implementation_name',), [
    ('as_iterator_limited',),
    ('as_iterator_limited_alt',),
])
class TestAsIteratorLimited(_NamedImplementationTestCase):
    """
    Tests for the as_iterator_limited and as_iterator_limited_alt functions.
    """

    __slots__ = ()

    def test_iterator_calls_simple_f_until_sentinel(self):
        d = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'e'}
        k = 'a'

        def f():
            nonlocal k
            k = d[k]
            return k

        it = self.implementation(f, 'd')
        self.assertEqual(next(it), 'b')
        self.assertEqual(next(it), 'c')
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

        Calling as_iterator_limited{_alt} on synthesized functions that
        themselves behave like calling next() on an iterator behaves as
        expected.
        """
        f_impl = getattr(functions, f_name)
        it = self.implementation(f_impl(), sentinel)
        self.assertIsInstance(it, Iterator)
        self.assertListEqual(list(it), expected)


@functools.cache
def _fib5k():
    """Return a list of the first 5000 Fibonacci numbers, read from a file."""
    with open('fib5k.txt', encoding='utf-8') as file:
        return list(map(int, file))


if __name__ == '__main__':
    unittest.main()
