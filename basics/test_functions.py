#!/usr/bin/env python

"""Tests for the functions in functions.py."""

from collections.abc import Iterator
import contextlib
import functools
import io
import itertools
import sys
import unittest

from parameterized import parameterized, parameterized_class

import fibonacci
import functions
import recursion

_original_count_tree_nodes = functions.count_tree_nodes


class _IterableWithGeneratorIterator:
    """A non-iterator iterable whose iterator is a generator."""

    __slots__ = ('_start',)

    def __init__(self, start):
        self._start = start

    def __iter__(self):
        while True:
            yield self._start
            self._start += 1


class _CloseableNonGeneratorIterator:
    """An iterator that isn't a generator but has a similar close method."""

    __slots__ = ('_next_result',)

    def __init__(self, start=0):
        self._next_result = start

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

    def __iter__(self):
        return _CloseableNonGeneratorIterator(self._start)


@functools.cache
def _fib5k():
    """Return a list of the first 5000 Fibonacci numbers, read from a file."""
    with open('fib5k.txt', encoding='utf-8') as file:
        return list(map(int, file))


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
    ])
    def test_no_close_attribute_if_iterator_has_no_close(self, _name, it):
        f = functions.as_closeable_func(it)
        self.assertFalse(hasattr(f, 'close'))

    @parameterized.expand([
        ('itertools.count', itertools.count(1)),
        ('list iterator', iter([1, 2, 3])),
        ('list', [1, 2, 3]),
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
    ])
    def test_no_close_attribute_if_iterator_has_no_close(self, _name, it):
        f = functions.as_closeable_func_limited(it, -17)
        self.assertFalse(hasattr(f, 'close'))

    @parameterized.expand([
        ('itertools.count', itertools.count(1)),
        ('list iterator', iter([1, 2, 3])),
        ('list', [1, 2, 3]),
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
    ('as_closeable_iterator_limited',)
])
class TestAsIteratorLimited(_NamedImplementationTestCase):
    """Tests for as_iterator_limited and related functions."""

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

        Calling as_iterator_limited{_alt} on synthesized functions that
        themselves behave like calling next() on an iterator behaves as
        expected.
        """
        f_impl = getattr(functions, f_name)
        it = self.implementation(f_impl(), sentinel)
        with self.subTest('is an iterator'):
            self.assertIsInstance(it, Iterator)
        with self.subTest('has correct values'):
            self.assertListEqual(list(it), expected)


# FIXME: Write the TestAsCloseableIteratorLimited class here.


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


# FIXME: Write the AsCloseableIterator class here.


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


# FIXME: Write the TestFuncFilter class here.


if __name__ == '__main__':
    unittest.main()
